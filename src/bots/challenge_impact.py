"""Calculate the game impact of ABS challenges.

Uses run expectancy tables and count-based leverage to score how much
each overturned (or upheld) challenge mattered to the game outcome.

Impact factors:
1. Run Expectancy (RE24) swing from the count change
2. Score differential (close game = higher impact)
3. Inning (later = higher leverage)
4. Runners on base (more runners = higher impact)
"""

# 2024 MLB Run Expectancy Matrix (runs expected to score in remainder of inning)
# Rows: base state (000=empty, 100=1st, 010=2nd, etc.), Columns: 0/1/2 outs
RUN_EXPECTANCY = {
    #              0 outs   1 out    2 outs
    (0, 0, 0):  [0.481,   0.254,   0.098],  # bases empty
    (1, 0, 0):  [0.859,   0.509,   0.224],  # runner on 1st
    (0, 1, 0):  [1.100,   0.664,   0.319],  # runner on 2nd
    (1, 1, 0):  [1.437,   0.884,   0.429],  # 1st and 2nd
    (0, 0, 1):  [1.350,   0.950,   0.353],  # runner on 3rd
    (1, 0, 1):  [1.784,   1.130,   0.478],  # 1st and 3rd
    (0, 1, 1):  [1.964,   1.376,   0.580],  # 2nd and 3rd
    (1, 1, 1):  [2.282,   1.541,   0.752],  # bases loaded
}

# Expected run value change per count transition
# Going from one count to another changes the expected outcome of the PA.
# Positive = favors batter, negative = favors pitcher.
# Format: (balls, strikes) -> expected runs above average for the PA
COUNT_RUN_VALUES = {
    (0, 0):  0.000,
    (1, 0):  0.032,
    (0, 1): -0.036,
    (2, 0):  0.079,
    (1, 1): -0.010,
    (0, 2): -0.074,
    (3, 0):  0.167,
    (2, 1):  0.035,
    (1, 2): -0.050,
    (3, 1):  0.112,
    (2, 2): -0.024,
    (3, 2):  0.049,
}


def get_base_state(play):
    """Extract base runners from play data as (1st, 2nd, 3rd) tuple of 0/1."""
    runners = play.get("runners", [])
    # Look at the movement details to determine who was on base at pitch time
    # Alternatively, use the matchup/runners from the play start
    on_1b = 0
    on_2b = 0
    on_3b = 0

    for runner in runners:
        start = runner.get("movement", {}).get("originBase")
        if start == "1B":
            on_1b = 1
        elif start == "2B":
            on_2b = 1
        elif start == "3B":
            on_3b = 1

    return (on_1b, on_2b, on_3b)


def calculate_challenge_impact(challenge, play_data=None):
    """Calculate the impact score of an ABS challenge.

    Args:
        challenge: dict from find_challenges_in_game()
        play_data: the raw play dict from the API (for runner/count info)

    Returns:
        dict with impact metrics added to the challenge
    """
    impact = {}

    # -- Count impact --
    # If a called strike is overturned to a ball (or vice versa),
    # what's the run value swing?
    count = None
    outs = None
    base_state = (0, 0, 0)

    if play_data:
        # Get the count AT THE TIME of the challenge pitch
        # The event's count field shows the count AFTER the pitch
        events = play_data.get("playEvents", [])
        for ev in events:
            review = ev.get("reviewDetails")
            if review:
                count_data = ev.get("count", {})
                # Count BEFORE this pitch: subtract the result
                balls = count_data.get("balls", 0)
                strikes = count_data.get("strikes", 0)
                outs = count_data.get("outs", 0)

                call_code = challenge.get("call_code", "")
                # The count in the event is AFTER the pitch was called
                # So we need to figure out the pre-pitch count
                if call_code == "C":  # called strike
                    # After this pitch, strikes went up by 1
                    pre_strikes = max(0, strikes - 1)
                    pre_balls = balls
                elif call_code == "B":  # ball
                    pre_balls = max(0, balls - 1)
                    pre_strikes = strikes
                else:
                    pre_balls = balls
                    pre_strikes = strikes

                count = (pre_balls, pre_strikes)
                break

        base_state = get_base_state(play_data)
        if outs is None:
            outs = play_data.get("count", {}).get("outs", 0)

    # Calculate count swing
    if count:
        # What the count would be with original call vs overturned call
        if challenge.get("call_code") == "C":
            # Originally called strike. If overturned, it becomes a ball.
            with_strike = (count[0], min(count[1] + 1, 2))
            with_ball = (min(count[0] + 1, 3), count[1])
        elif challenge.get("call_code") == "B":
            # Originally called ball. If overturned, it becomes a strike.
            with_ball = (min(count[0] + 1, 3), count[1])
            with_strike = (count[0], min(count[1] + 1, 2))
        else:
            with_strike = count
            with_ball = count

        rv_strike = COUNT_RUN_VALUES.get(with_strike, 0)
        rv_ball = COUNT_RUN_VALUES.get(with_ball, 0)

        # The swing is the difference between the two outcomes
        count_swing = abs(rv_ball - rv_strike)
        impact["count_before"] = f"{count[0]}-{count[1]}"
        impact["count_if_strike"] = f"{with_strike[0]}-{with_strike[1]}"
        impact["count_if_ball"] = f"{with_ball[0]}-{with_ball[1]}"
        impact["count_rv_swing"] = round(count_swing, 3)
    else:
        impact["count_rv_swing"] = 0

    # -- Base/out RE impact --
    if base_state in RUN_EXPECTANCY and outs is not None and outs < 3:
        re = RUN_EXPECTANCY[base_state][outs]
        impact["run_expectancy"] = round(re, 3)

        # More runners = higher base impact multiplier
        runners_on = sum(base_state)
        impact["runners_on"] = runners_on
    else:
        impact["run_expectancy"] = 0
        impact["runners_on"] = 0

    # -- Leverage multiplier --
    inning = challenge.get("inning", 1)
    # Later innings have higher leverage
    inning_mult = 1.0 + max(0, (inning - 5)) * 0.15  # ramps up after 5th

    # Close game multiplier
    away_score = challenge.get("away_score", 0) or 0
    home_score = challenge.get("home_score", 0) or 0
    score_diff = abs(away_score - home_score)

    if score_diff == 0:
        close_game_mult = 1.3  # Tied game
    elif score_diff == 1:
        close_game_mult = 1.2  # 1-run game
    elif score_diff == 2:
        close_game_mult = 1.1  # 2-run game
    else:
        close_game_mult = 0.8  # 3+ run lead

    # -- Composite impact score --
    # Weighted combination: count swing is the core, multiplied by situation
    base_mult = 1.0 + impact["runners_on"] * 0.3
    composite = impact["count_rv_swing"] * base_mult * inning_mult * close_game_mult

    # Normalize to a 1-100 scale (roughly)
    impact["impact_score"] = round(min(100, composite * 500), 1)
    impact["inning_multiplier"] = round(inning_mult, 2)

    # Qualitative label
    score = impact["impact_score"]
    if score >= 60:
        impact["impact_label"] = "HIGH"
    elif score >= 30:
        impact["impact_label"] = "MEDIUM"
    else:
        impact["impact_label"] = "LOW"

    return impact


def rank_challenges_by_impact(challenges_with_impact):
    """Sort challenges by impact score, return top N."""
    return sorted(challenges_with_impact,
                  key=lambda c: c.get("impact", {}).get("impact_score", 0),
                  reverse=True)
