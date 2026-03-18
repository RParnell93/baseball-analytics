"""MLB live game feed poller.

Shared infrastructure for bots that react to live game events.
Polls the MLB Stats API game feeds and yields events of interest.
"""

import time
import statsapi
import json
from datetime import date


def get_todays_games():
    """Get all games scheduled for today."""
    today = date.today().strftime("%m/%d/%Y")
    return statsapi.schedule(start_date=today, end_date=today)


def get_live_game_ids():
    """Get game IDs for games currently in progress."""
    games = get_todays_games()
    return [g["game_id"] for g in games if g["status"] in ("In Progress", "Live")]


def get_game_feed(game_id):
    """Fetch the full live game feed."""
    return statsapi.get("game", {"gamePk": game_id})


def get_play_events(feed):
    """Extract all plays with their events from a game feed."""
    return feed["liveData"]["plays"]["allPlays"]


def get_umpire_hp(feed):
    """Get the home plate umpire name from the game feed."""
    officials = feed["liveData"].get("boxscore", {}).get("officials", [])
    for ump in officials:
        if ump.get("officialType") == "Home Plate":
            return ump.get("official", {}).get("fullName", "Unknown")
    return "Unknown"


def get_pitch_data(play_event):
    """Extract pitch location and details from a play event.

    Returns dict with pX, pZ, zone, call description, pitch type, velocity.
    """
    pitch_data = play_event.get("pitchData", {})
    details = play_event.get("details", {})
    coords = pitch_data.get("coordinates", {})

    return {
        "pX": coords.get("pX"),
        "pZ": coords.get("pZ"),
        "zone": pitch_data.get("zone"),
        "call": details.get("description", ""),
        "call_code": details.get("code", ""),
        "pitch_type": details.get("type", {}).get("code", ""),
        "pitch_name": details.get("type", {}).get("description", ""),
        "speed": pitch_data.get("startSpeed"),
        "strike_zone_top": pitch_data.get("strikeZoneTop"),
        "strike_zone_bottom": pitch_data.get("strikeZoneBottom"),
    }


def get_matchup_info(play):
    """Extract batter/pitcher info from a play."""
    matchup = play.get("matchup", {})
    return {
        "batter_name": matchup.get("batter", {}).get("fullName", "Unknown"),
        "batter_id": matchup.get("batter", {}).get("id"),
        "pitcher_name": matchup.get("pitcher", {}).get("fullName", "Unknown"),
        "pitcher_id": matchup.get("pitcher", {}).get("id"),
        "bat_side": matchup.get("batSide", {}).get("code", ""),
        "pitch_hand": matchup.get("pitchHand", {}).get("code", ""),
    }


class LiveGamePoller:
    """Polls live game feeds and tracks seen events.

    Usage:
        poller = LiveGamePoller(interval=15)
        for event in poller.poll():
            # event is a dict with game info, play, and event details
            handle_event(event)
    """

    def __init__(self, interval=15, event_filter=None):
        """
        Args:
            interval: seconds between polls
            event_filter: callable(play_event) -> bool, return True to yield
        """
        self.interval = interval
        self.event_filter = event_filter
        # Track (game_id, play_index, event_index) to avoid duplicates
        self.seen_events = set()

    def poll_once(self):
        """Poll all live games once and return new events."""
        new_events = []
        live_ids = get_live_game_ids()

        for gid in live_ids:
            try:
                feed = get_game_feed(gid)
            except Exception:
                continue

            game_data = feed.get("gameData", {})
            away = game_data.get("teams", {}).get("away", {}).get("abbreviation", "")
            home = game_data.get("teams", {}).get("home", {}).get("abbreviation", "")
            umpire_hp = get_umpire_hp(feed)

            plays = get_play_events(feed)
            for play_idx, play in enumerate(plays):
                matchup = get_matchup_info(play)
                for ev_idx, ev in enumerate(play.get("playEvents", [])):
                    key = (gid, play_idx, ev_idx)
                    if key in self.seen_events:
                        continue
                    self.seen_events.add(key)

                    if self.event_filter and not self.event_filter(ev):
                        continue

                    pitch = get_pitch_data(ev)
                    new_events.append({
                        "game_id": gid,
                        "away": away,
                        "home": home,
                        "umpire_hp": umpire_hp,
                        "inning": play.get("about", {}).get("inning"),
                        "half": play.get("about", {}).get("halfInning"),
                        "matchup": matchup,
                        "pitch": pitch,
                        "event": ev,
                        "play": play,
                    })

        return new_events

    def poll(self):
        """Generator that continuously polls and yields new events."""
        print(f"Polling live games every {self.interval}s...")
        while True:
            try:
                events = self.poll_once()
                for ev in events:
                    yield ev
            except KeyboardInterrupt:
                print("Stopped.")
                return
            except Exception as e:
                print(f"Poll error: {e}")

            time.sleep(self.interval)
