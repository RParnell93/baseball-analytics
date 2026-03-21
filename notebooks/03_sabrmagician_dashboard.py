import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import os
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px

    # @sabrmagician dark theme
    THEME = {
        "bg": "#0e1117",
        "card": "#1a1a2e",
        "text": "#e0e0e0",
        "muted": "#8892a0",
        "accent": "#FF6B35",
        "teal": "#4ECDC4",
        "green": "#2ECC71",
        "red": "#E74C3C",
        "gold": "#F1C40F",
        "grid": "#2d2d44",
    }

    LAYOUT = dict(
        paper_bgcolor=THEME["bg"],
        plot_bgcolor=THEME["card"],
        font=dict(family="Helvetica Neue, Arial", color=THEME["text"]),
        margin=dict(t=80, b=60, l=60, r=40),
    )

    CREDIT = "@sabrmagician"

    mo.md("""# @sabrmagician MLB Analytics Dashboard

    Five visualizations filling gaps in the baseball analytics landscape.
    Each chart represents content nobody else is producing.""")
    return CREDIT, LAYOUT, THEME, duckdb, go, mo, np, os, pd, px


@app.cell
def _(duckdb, os):
    _password = os.environ.get("MOTHERDUCK_TOKEN")
    con = duckdb.connect("md:baseball", config={"motherduck_token": _password})
    return (con,)


# ── 1. ABS Challenge Impact Zone Map ────────────────────────────────────────
# Gap: No automated, visually consistent ABS challenge content exists.
# This is the UmpScorecards play for the ABS era.

@app.cell
def _(con, mo):
    try:
        _umpires = con.execute("""
            SELECT umpire, COUNT(*) as challenges,
                   ROUND(SUM(CASE WHEN result = 'overturned' THEN 1 ELSE 0 END)::FLOAT
                         / COUNT(*) * 100, 1) as overturn_pct
            FROM abs_challenges
            WHERE pX IS NOT NULL AND pZ IS NOT NULL
            GROUP BY umpire
            HAVING COUNT(*) >= 5
            ORDER BY challenges DESC
        """).fetchdf()

        _opts = {"All Umpires": "all"}
        for _, r in _umpires.iterrows():
            _opts[f"{r['umpire']} ({int(r['challenges'])} ch, {r['overturn_pct']}% OT)"] = r["umpire"]

        ump_select = mo.ui.dropdown(options=_opts, value="all", label="Filter by Umpire")
    except Exception:
        ump_select = mo.ui.dropdown(options={"No ABS data": "none"}, value="none", label="")

    mo.md("## 1. ABS Challenge Zone Map\n*Nobody produces daily ABS challenge scorecards. This is the first-mover content play.*")
    ump_select
    return (ump_select,)


@app.cell
def _(con, ump_select, CREDIT, LAYOUT, THEME, go, np, mo):
    if ump_select.value == "none":
        mo.md("*abs_challenges table not found. Push challenge data to MotherDuck first.*")
    else:
        _ump_val = ump_select.value.replace("'", "''")
        _where = f"AND umpire = '{_ump_val}'" if ump_select.value != "all" else ""
        _data = con.execute(f"""
            SELECT pX, pZ, sz_top, sz_bottom, result, impact_score,
                   challenge_team, umpire, pitch_name, speed,
                   balls, strikes, batter, pitcher
            FROM abs_challenges
            WHERE pX IS NOT NULL AND pZ IS NOT NULL {_where}
        """).fetchdf()

        _total = len(_data)
        _ot = (_data["result"] == "overturned").sum()
        _rate = _ot / _total * 100 if _total > 0 else 0
        _over = _data[_data["result"] == "overturned"]
        _upheld = _data[_data["result"] == "upheld"]
        _sz_top = _data["sz_top"].mean()
        _sz_bot = _data["sz_bottom"].mean()

        fig = go.Figure()

        # Strike zone rectangle + 9-box grid
        fig.add_shape(type="rect", x0=-0.83, x1=0.83, y0=_sz_bot, y1=_sz_top,
                      line=dict(color=THEME["muted"], width=2),
                      fillcolor="rgba(74,78,105,0.15)")
        _w = 0.83 * 2 / 3
        _h = (_sz_top - _sz_bot) / 3
        for i in range(1, 3):
            fig.add_shape(type="line", x0=-0.83 + i * _w, x1=-0.83 + i * _w,
                          y0=_sz_bot, y1=_sz_top,
                          line=dict(color=THEME["grid"], width=1, dash="dot"))
            fig.add_shape(type="line", x0=-0.83, x1=0.83,
                          y0=_sz_bot + i * _h, y1=_sz_bot + i * _h,
                          line=dict(color=THEME["grid"], width=1, dash="dot"))

        for _subset, _color, _label in [
            (_over, "#4A90D9", "Overturned"),
            (_upheld, "#E8553D", "Upheld"),
        ]:
            if len(_subset) == 0:
                continue
            _imp = _subset["impact_score"].fillna(30)
            fig.add_trace(go.Scatter(
                x=_subset["pX"], y=_subset["pZ"], mode="markers",
                marker=dict(
                    size=np.clip(_imp / 5, 5, 18), color=_color,
                    opacity=0.6, line=dict(width=0.5, color="white"),
                ),
                name=f"{_label} ({len(_subset)})",
                customdata=np.column_stack([
                    _subset["batter"].values, _subset["pitcher"].values,
                    _subset["pitch_name"].values, _subset["speed"].values,
                    _subset["balls"].values, _subset["strikes"].values,
                    _imp.values,
                ]),
                hovertemplate=(
                    f"<b>{_label.upper()}</b><br>"
                    "%{customdata[0]} vs %{customdata[1]}<br>"
                    "Pitch: %{customdata[2]} (%{customdata[3]:.0f} mph)<br>"
                    "Count: %{customdata[4]:.0f}-%{customdata[5]:.0f} | "
                    "Impact: %{customdata[6]:.0f}<extra></extra>"
                ),
            ))

        _title_ump = ump_select.value if ump_select.value != "all" else "Spring Training 2026"
        fig.update_layout(
            **LAYOUT,
            title=dict(
                text=(f"ABS Challenge Zone Map - {_title_ump}"
                      f"<br><sub>{_total} challenges | {_rate:.0f}% overturn rate</sub>"),
                font=dict(size=20, color=THEME["text"]),
                x=0.5, xanchor="center",
            ),
            xaxis=dict(
                title="Horizontal Location (ft)", range=[-2, 2], dtick=0.5,
                gridcolor=THEME["grid"], zerolinecolor=THEME["grid"],
                scaleanchor="y",
            ),
            yaxis=dict(
                title="Vertical Location (ft)", range=[0, 5], dtick=0.5,
                gridcolor=THEME["grid"], zerolinecolor=THEME["grid"],
            ),
            height=700,
            legend=dict(
                orientation="h", yanchor="top", y=-0.05,
                xanchor="center", x=0.5, font=dict(size=12),
            ),
            annotations=[
                dict(x=1.8, y=0.3, text=CREDIT, showarrow=False,
                     font=dict(size=9, color=THEME["muted"])),
            ],
        )

        mo.ui.plotly(fig)
    return


# ── 2. Pitcher Stuff+ Arsenal Card ─────────────────────────────────────────
# Gap: Nobody makes clean, consistent pitch arsenal quality graphics.
# Pitcher List owns pitcher visuals but doesn't use Stuff+/Location+/Pitching+.

@app.cell
def _(con, mo):
    _pitchers = con.execute("""
        SELECT Name, Team, IDfg,
               "Stuff+" as stuff, "Location+" as loc, "Pitching+" as pit,
               IP, SO, ERA
        FROM fg_pitching
        WHERE Season = 2024 AND IP >= 80 AND "Stuff+" IS NOT NULL
        ORDER BY "Stuff+" DESC
    """).fetchdf()

    _opts = {
        f"{r['Name']} ({r['Team']}) Stf+{r['stuff']:.0f}": str(r["IDfg"])
        for _, r in _pitchers.iterrows()
    }
    stuff_select = mo.ui.dropdown(
        options=_opts,
        value=str(_pitchers.iloc[0]["IDfg"]),
        label="Select Pitcher",
    )

    mo.md("## 2. Pitcher Stuff+ Arsenal Card\n"
           "*FanGraphs' Stuff+/Location+/Pitching+ models rate every pitch. "
           "Nobody makes these shareable yet.*")
    stuff_select
    return (stuff_select,)


@app.cell
def _(con, stuff_select, CREDIT, LAYOUT, THEME, go, mo, pd):
    _pid = int(stuff_select.value)
    _pitcher = con.execute(
        f"SELECT * FROM fg_pitching WHERE IDfg = {_pid} AND Season = 2024"
    ).fetchdf()

    if len(_pitcher) == 0:
        mo.md("*Pitcher not found.*")
    else:
        _row = _pitcher.iloc[0]
        _name = _row["Name"]
        _team = _row["Team"]

        _pitch_map = {
            "4-Seam": ("Stf+ FA", "FA% (sc)", "vFA (sc)"),
            "Sinker": ("Stf+ SI", "SI% (sc)", "vSI (sc)"),
            "Cutter": ("Stf+ FC", "FC% (sc)", "vFC (sc)"),
            "Slider": ("Stf+ SL", "SL% (sc)", "vSL (sc)"),
            "Curveball": ("Stf+ CU", "CU% (sc)", "vCU (sc)"),
            "Changeup": ("Stf+ CH", "CH% (sc)", "vCH (sc)"),
            "Sweeper": ("Stf+ ST", "ST% (sc)", "vST (sc)"),
            "Splitter": ("Stf+ FS", "FS% (sc)", "vFS (sc)"),
            "Knuckle Curve": ("Stf+ KC", "KC% (sc)", "vKC (sc)"),
            "Slurve": ("Stf+ SV", "SV% (sc)", "vSV (sc)"),
        }

        _data = []
        for pname, (stf_col, use_col, vel_col) in _pitch_map.items():
            _stf = _row.get(stf_col)
            _use = _row.get(use_col)
            _vel = _row.get(vel_col)
            if pd.notna(_stf) and pd.notna(_use) and _use > 0:
                _data.append({
                    "pitch": pname,
                    "stuff": float(_stf),
                    "usage": float(_use) * 100,
                    "velo": float(_vel) if pd.notna(_vel) else 0,
                })

        if not _data:
            mo.md("*No pitch-level Stuff+ data available for this pitcher.*")
        else:
            _df = pd.DataFrame(_data).sort_values("usage", ascending=True)
            _colors = [
                "#4A90D9" if s >= 100 else "#E8553D"
                for s in _df["stuff"]
            ]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=_df["pitch"],
                x=_df["stuff"] - 100,
                orientation="h",
                marker=dict(color=_colors, opacity=0.85,
                            line=dict(width=1, color="white")),
                text=_df.apply(
                    lambda r: f"  {r['stuff']:.0f}  |  {r['usage']:.0f}%  |  {r['velo']:.1f} mph",
                    axis=1,
                ),
                textposition="outside",
                textfont=dict(size=11, color=THEME["text"]),
                hovertemplate=(
                    "<b>%{y}</b><br>Stuff+: %{customdata[0]:.0f}<br>"
                    "Usage: %{customdata[1]:.0f}%<br>"
                    "Velo: %{customdata[2]:.1f} mph<extra></extra>"
                ),
                customdata=list(zip(
                    _df["stuff"], _df["usage"], _df["velo"]
                )),
            ))

            fig.add_vline(x=0, line=dict(color=THEME["gold"], width=2, dash="dash"))

            _stf_all = _row.get("Stuff+", "?")
            _loc_all = _row.get("Location+", "?")
            _pit_all = _row.get("Pitching+", "?")

            fig.update_layout(
                **LAYOUT,
                title=dict(
                    text=f"{_name} ({_team}) - Pitch Arsenal Quality",
                    font=dict(size=20, color=THEME["text"]),
                    x=0.5, xanchor="center",
                ),
                xaxis=dict(
                    title="Stuff+ (deviation from 100 = avg)",
                    gridcolor=THEME["grid"],
                    zerolinecolor=THEME["gold"],
                ),
                yaxis=dict(gridcolor=THEME["grid"]),
                height=max(350, len(_data) * 65 + 150),
                annotations=[
                    dict(
                        x=0.98, y=0.02, xref="paper", yref="paper",
                        text=CREDIT, showarrow=False,
                        font=dict(size=9, color=THEME["muted"]),
                    ),
                    dict(
                        x=0.02, y=0.98, xref="paper", yref="paper",
                        text=f"Overall: Stf+ {_stf_all} | Loc+ {_loc_all} | Pit+ {_pit_all}",
                        showarrow=False,
                        font=dict(size=11, color=THEME["accent"]),
                        xanchor="left", yanchor="top",
                    ),
                ],
            )

            mo.ui.plotly(fig)
    return


# ── 3. Player 360 - Cross-Platform Profile ─────────────────────────────────
# Gap: No single view combines Statcast + FanGraphs + Ottoneu data.
# Our DuckDB backend already links these; this makes it visual.

@app.cell
def _(con, mo):
    _batters = con.execute("""
        SELECT Name, Team, PA, IDfg, "wRC+" as wrc
        FROM fg_batting
        WHERE Season = 2024 AND PA >= 400
        ORDER BY "wRC+" DESC
    """).fetchdf()

    _opts = {
        f"{r['Name']} ({r['Team']}) {r['wrc']:.0f} wRC+": str(r["IDfg"])
        for _, r in _batters.iterrows()
    }
    p360_select = mo.ui.dropdown(
        options=_opts,
        value=str(_batters.iloc[0]["IDfg"]),
        label="Select Batter",
    )

    mo.md("## 3. Player 360 Profile\n"
           "*Statcast percentiles + FanGraphs advanced stats + Ottoneu salary in one view. "
           "Nobody else integrates all three.*")
    p360_select
    return (p360_select,)


@app.cell
def _(con, p360_select, CREDIT, LAYOUT, THEME, go, mo, pd):
    _fgid = int(p360_select.value)

    _fg = con.execute(f"""
        SELECT Name, Team, PA, HR, SB, AVG, OBP, SLG, ISO, BABIP,
               "wRC+" as wrc_plus, wOBA as woba, WAR,
               "K%" as k_pct, "BB%" as bb_pct, "SwStr%" as swstr,
               "Barrel%" as barrel_pct, "HardHit%" as hardhit_pct,
               EV as avg_ev, maxEV as max_ev
        FROM fg_batting
        WHERE IDfg = {_fgid} AND Season = 2024
    """).fetchdf()

    _otto = con.execute(f"""
        SELECT "Avg Salary", "Position(s)"
        FROM ottoneu_sabr_values
        WHERE CAST("FG MajorLeagueID" AS INT) = {_fgid}
    """).fetchdf()

    if len(_fg) == 0:
        mo.md("*Player not found in 2024 data.*")
    else:
        _p = _fg.iloc[0]
        _salary = _otto.iloc[0]["Avg Salary"] if len(_otto) > 0 else "N/A"
        _pos = _otto.iloc[0]["Position(s)"] if len(_otto) > 0 else "?"

        # League distribution for percentile calculation
        _league = con.execute("""
            SELECT "wRC+" as wrc_plus, wOBA as woba,
                   "K%" as k_pct, "BB%" as bb_pct,
                   "Barrel%" as barrel_pct, "HardHit%" as hardhit_pct,
                   EV as avg_ev, maxEV as max_ev, ISO, "SwStr%" as swstr
            FROM fg_batting
            WHERE Season = 2024 AND PA >= 400
        """).fetchdf()

        def _pctile(stat, val, reverse=False):
            if pd.isna(val) or stat not in _league.columns:
                return 50
            col = _league[stat].dropna()
            if len(col) == 0:
                return 50
            pct = (col < val).sum() / len(col) * 100
            return 100 - pct if reverse else pct

        _metrics = [
            ("wRC+", _p.get("wrc_plus"), False),
            ("wOBA", _p.get("woba"), False),
            ("Barrel%", _p.get("barrel_pct"), False),
            ("HardHit%", _p.get("hardhit_pct"), False),
            ("Avg EV", _p.get("avg_ev"), False),
            ("Max EV", _p.get("max_ev"), False),
            ("K%", _p.get("k_pct"), True),
            ("BB%", _p.get("bb_pct"), False),
            ("ISO", _p.get("ISO"), False),
            ("SwStr%", _p.get("swstr"), True),
        ]

        _names = [m[0] for m in _metrics][::-1]
        _vals = [m[1] for m in _metrics][::-1]
        _revs = [m[2] for m in _metrics][::-1]
        _pctiles = [
            _pctile(n.lower().replace("+", "_plus").replace("%", "_pct")
                    if n not in ("wRC+", "wOBA", "Avg EV", "Max EV", "ISO")
                    else {"wRC+": "wrc_plus", "wOBA": "woba", "Avg EV": "avg_ev",
                          "Max EV": "max_ev", "ISO": "ISO"}.get(n, n),
                    v, r)
            for n, v, r in zip(_names, _vals, _revs)
        ]

        def _pct_color(p):
            if p >= 90:
                return "#1565C0"
            if p >= 70:
                return "#4A90D9"
            if p >= 40:
                return THEME["gold"]
            if p >= 20:
                return THEME["accent"]
            return "#E8553D"

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=_names, x=_pctiles, orientation="h",
            marker=dict(
                color=[_pct_color(p) for p in _pctiles],
                opacity=0.9,
                line=dict(width=0.5, color="white"),
            ),
            text=[
                f"  {v:.3f} ({p:.0f}th)" if pd.notna(v) and isinstance(v, float) and abs(v) < 2
                else f"  {v:.1f} ({p:.0f}th)" if pd.notna(v)
                else "  N/A"
                for v, p in zip(_vals, _pctiles)
            ],
            textposition="outside",
            textfont=dict(size=10, color=THEME["text"]),
        ))

        _war = _p.get("WAR", "?")
        _avg_str = f"{_p['AVG']:.3f}" if pd.notna(_p.get("AVG")) else "?"
        fig.update_layout(
            **LAYOUT,
            title=dict(
                text=f"{_p['Name']} ({_p['Team']}) - Player 360",
                font=dict(size=20, color=THEME["text"]),
                x=0.5, xanchor="center",
            ),
            xaxis=dict(
                title="Percentile (vs 400+ PA)", range=[0, 115],
                dtick=25, gridcolor=THEME["grid"],
            ),
            yaxis=dict(gridcolor=THEME["grid"]),
            height=500,
            annotations=[
                dict(
                    x=0.98, y=0.02, xref="paper", yref="paper",
                    text=CREDIT, showarrow=False,
                    font=dict(size=9, color=THEME["muted"]),
                ),
                dict(
                    x=0.02, y=0.98, xref="paper", yref="paper",
                    text=(f"{_pos} | SABR: {_salary} | {_p['PA']} PA | "
                          f"{_p['HR']} HR | {_p['SB']} SB | {_avg_str} AVG | "
                          f"{_war} WAR"),
                    showarrow=False,
                    font=dict(size=10, color=THEME["accent"]),
                    xanchor="left", yanchor="top",
                ),
            ],
        )

        mo.ui.plotly(fig)
    return


# ── 4. Bat Tracking: Speed vs Swing Length ──────────────────────────────────
# Gap: Savant added bat tracking in 2024 but hasn't built visual explainers.

@app.cell
def _(con, CREDIT, LAYOUT, THEME, go, mo, np, pd):
    try:
        _bt = con.execute("""
            WITH bt AS (
                SELECT
                    batter,
                    AVG(bat_speed) as avg_bat_speed,
                    AVG(swing_length) as avg_swing_length,
                    AVG(launch_speed)
                        FILTER (WHERE launch_speed IS NOT NULL) as avg_ev,
                    COUNT(*)
                        FILTER (WHERE bat_speed IS NOT NULL) as swings,
                    AVG(CASE WHEN barrel = 1 THEN 1.0 ELSE 0.0 END)
                        FILTER (WHERE launch_speed IS NOT NULL) as barrel_rate
                FROM statcast_pitches
                WHERE bat_speed IS NOT NULL
                GROUP BY batter
                HAVING COUNT(*) FILTER (WHERE bat_speed IS NOT NULL) >= 100
            )
            SELECT
                bt.*,
                COALESCE(
                    p.name_first || ' ' || p.name_last,
                    'ID ' || bt.batter
                ) as player_name,
                fg."wRC+" as wrc_plus
            FROM bt
            LEFT JOIN player_ids p
                ON CAST(bt.batter AS INTEGER) = CAST(p.key_mlbam AS INTEGER)
            LEFT JOIN fg_batting fg
                ON CAST(p.key_fangraphs AS VARCHAR) = CAST(fg.IDfg AS VARCHAR)
                AND fg.Season = 2024
            WHERE fg.PA >= 200
            ORDER BY avg_bat_speed DESC
        """).fetchdf()

        if len(_bt) < 10:
            raise ValueError(f"Only {len(_bt)} qualified hitters with bat tracking")

        _med_speed = _bt["avg_bat_speed"].median()
        _med_length = _bt["avg_swing_length"].median()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=_bt["avg_bat_speed"],
            y=_bt["avg_swing_length"],
            mode="markers",
            text=_bt["player_name"],
            marker=dict(
                size=10,
                color=_bt["avg_ev"].fillna(85),
                colorscale=[[0, "#3498DB"], [0.5, "#F1C40F"], [1, THEME["red"]]],
                cmin=83, cmax=94,
                colorbar=dict(title="Avg EV<br>(mph)", len=0.6),
                line=dict(width=0.5, color="white"),
                opacity=0.8,
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Bat Speed: %{x:.1f} mph<br>"
                "Swing Length: %{y:.2f} ft<br>"
                "Avg EV: %{customdata[0]:.1f} mph<br>"
                "wRC+: %{customdata[1]:.0f}<br>"
                "Barrel%: %{customdata[2]:.1%}<extra></extra>"
            ),
            customdata=list(zip(
                _bt["avg_ev"].fillna(0),
                _bt["wrc_plus"].fillna(0),
                _bt["barrel_rate"].fillna(0),
            )),
        ))

        fig.add_hline(y=_med_length,
                      line=dict(color=THEME["gold"], width=1, dash="dot"))
        fig.add_vline(x=_med_speed,
                      line=dict(color=THEME["gold"], width=1, dash="dot"))

        fig.update_layout(
            **LAYOUT,
            title=dict(
                text="Bat Tracking: Speed vs Swing Length (2024)",
                font=dict(size=20, color=THEME["text"]),
                x=0.5, xanchor="center",
            ),
            xaxis=dict(title="Avg Bat Speed (mph)", gridcolor=THEME["grid"]),
            yaxis=dict(title="Avg Swing Length (ft)", gridcolor=THEME["grid"]),
            height=650,
            annotations=[
                dict(x=0.98, y=0.02, xref="paper", yref="paper",
                     text=CREDIT, showarrow=False,
                     font=dict(size=11, color=THEME["muted"])),
                dict(x=0.02, y=0.98, xref="paper", yref="paper",
                     text="Compact & Fast", showarrow=False,
                     font=dict(size=10, color=THEME["green"]),
                     xanchor="left", yanchor="top"),
                dict(x=0.98, y=0.98, xref="paper", yref="paper",
                     text="Long & Fast", showarrow=False,
                     font=dict(size=10, color=THEME["accent"]),
                     xanchor="right", yanchor="top"),
                dict(x=0.02, y=0.05, xref="paper", yref="paper",
                     text="Compact & Slow", showarrow=False,
                     font=dict(size=10, color=THEME["teal"]),
                     xanchor="left"),
                dict(x=0.98, y=0.05, xref="paper", yref="paper",
                     text="Long & Slow", showarrow=False,
                     font=dict(size=10, color=THEME["red"]),
                     xanchor="right"),
                dict(x=0.5, y=-0.08, xref="paper", yref="paper",
                     text=("Bubble color = avg exit velocity. "
                           "Dashed lines = median. 200+ PA, 100+ tracked swings."),
                     showarrow=False,
                     font=dict(size=9, color=THEME["muted"]),
                     xanchor="center"),
            ],
        )

        mo.md("## 4. Bat Tracking Explorer\n"
               "*Savant added bat tracking in 2024 but hasn't built visual explainers around it.*")
        mo.ui.plotly(fig)

    except Exception as e:
        mo.md(f"## 4. Bat Tracking Explorer\n\n"
               f"*Bat tracking data not available: {e}*\n\n"
               f"Requires 2024 Statcast data with bat_speed/swing_length columns.")
    return


# ── 5. Statcast Park Factor Impact ─────────────────────────────────────────
# Gap: Ballpark Pal has park models but locks them behind a paywall.
# This is free, visual, shareable - computed from public Statcast data.

@app.cell
def _(con, CREDIT, LAYOUT, THEME, go, mo):
    _pf = con.execute("""
        WITH park_stats AS (
            SELECT
                home_team,
                COUNT(*) as total_pitches,
                AVG(launch_speed)
                    FILTER (WHERE launch_speed IS NOT NULL
                            AND launch_speed >= 50) as avg_ev,
                SUM(CASE WHEN events = 'home_run' THEN 1 ELSE 0 END)::FLOAT
                    / NULLIF(SUM(CASE WHEN launch_speed IS NOT NULL
                                      THEN 1 ELSE 0 END), 0) as hr_per_bip,
                SUM(CASE WHEN events IN ('single','double','triple','home_run')
                         THEN 1 ELSE 0 END)::FLOAT
                    / NULLIF(SUM(CASE WHEN events IS NOT NULL
                                      THEN 1 ELSE 0 END), 0) as hit_rate
            FROM statcast_pitches
            WHERE home_team IS NOT NULL
            GROUP BY home_team
            HAVING COUNT(*) >= 5000
        ),
        league_avg AS (
            SELECT AVG(hr_per_bip) as lg_hr, AVG(hit_rate) as lg_hit
            FROM park_stats
        )
        SELECT
            p.home_team,
            ROUND((p.hr_per_bip / la.lg_hr - 1) * 100, 1) as hr_factor,
            ROUND((p.hit_rate / la.lg_hit - 1) * 100, 1) as hit_factor,
            ROUND(p.avg_ev, 1) as avg_ev
        FROM park_stats p, league_avg la
        ORDER BY hr_factor DESC
    """).fetchdf()

    if len(_pf) == 0:
        mo.md("## 5. Statcast Park Factor Impact\n\n*Could not compute park factors.*")
    else:
        _pf = _pf.sort_values("hr_factor", ascending=True)
        _colors = [
            "#E8553D" if x > 0 else "#4A90D9"
            for x in _pf["hr_factor"]
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=_pf["home_team"],
            x=_pf["hr_factor"],
            orientation="h",
            marker=dict(color=_colors, opacity=0.85,
                        line=dict(width=0.5, color="white")),
            text=_pf["hr_factor"].apply(
                lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%"
            ),
            textposition="outside",
            textfont=dict(size=9, color=THEME["text"]),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "HR Factor: %{x:+.1f}%<br>"
                "Hit Factor: %{customdata[0]:+.1f}%<br>"
                "Avg EV: %{customdata[1]:.1f} mph<extra></extra>"
            ),
            customdata=list(zip(_pf["hit_factor"], _pf["avg_ev"])),
        ))

        fig.add_vline(x=0, line=dict(color=THEME["gold"], width=2))

        fig.update_layout(
            **LAYOUT,
            title=dict(
                text="Statcast Park HR Factor (2024)",
                font=dict(size=20, color=THEME["text"]),
                x=0.5, xanchor="center",
            ),
            xaxis=dict(
                title="HR Rate vs League Average (%)",
                gridcolor=THEME["grid"],
                zerolinecolor=THEME["gold"],
            ),
            yaxis=dict(gridcolor=THEME["grid"]),
            height=max(500, len(_pf) * 22 + 150),
            annotations=[
                dict(x=0.98, y=0.02, xref="paper", yref="paper",
                     text=CREDIT, showarrow=False,
                     font=dict(size=11, color=THEME["muted"])),
                dict(x=0.5, y=-0.06, xref="paper", yref="paper",
                     text=("Computed from 2024 Statcast batted balls. "
                           "Red = hitter-friendly, teal = pitcher-friendly."),
                     showarrow=False,
                     font=dict(size=9, color=THEME["muted"]),
                     xanchor="center"),
            ],
        )

        mo.md("## 5. Statcast Park Factor Impact\n"
               "*Ballpark Pal locks park models behind a paywall. "
               "This is free, visual, shareable.*")
        mo.ui.plotly(fig)
    return


if __name__ == "__main__":
    app.run()
