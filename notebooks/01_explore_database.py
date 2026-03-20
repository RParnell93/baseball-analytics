import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import os
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    mo.md("# Baseball Analytics - Database Explorer\n\nExplore the data loaded into our DuckDB database.")
    return duckdb, go, mo, os, pd, px


@app.cell
def _(duckdb, os):
    _password = os.environ.get("MOTHERDUCK_TOKEN")
    con = duckdb.connect("md:baseball", config={"motherduck_token": _password})
    return (con,)


@app.cell
def _(con, mo, pd):
    # Show all tables
    tables = con.execute("SHOW TABLES").fetchdf()
    table_info = []
    for t in tables["name"]:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = len(con.execute(f"SELECT * FROM {t} LIMIT 0").description)
        table_info.append({"Table": t, "Rows": f"{count:,}", "Columns": cols})

    mo.md(f"""## Database Summary\n\n{pd.DataFrame(table_info).to_markdown(index=False)}""")
    return


@app.cell
def _(con, mo, px):
    # Top 20 hitters by FGPts in 2024
    top_hitters = con.execute("""
        SELECT Name, Team, PA, HR, SB, AVG, OBP, SLG,
               (AB * -1.0 + H * 5.6 + "2B" * 2.9 + "3B" * 5.7 + HR * 9.4 +
                BB * 3.0 + HBP * 3.0 + SB * 1.9 + CS * -2.8) as fgpts
        FROM fg_batting
        WHERE Season = 2024 AND PA >= 400
        ORDER BY fgpts DESC
        LIMIT 20
    """).fetchdf()

    fig = px.bar(
        top_hitters, x="Name", y="fgpts",
        color="fgpts", color_continuous_scale="YlOrRd",
        title="Top 20 Hitters by FGPts (2024, 400+ PA)",
        labels={"fgpts": "FanGraphs Points", "Name": ""},
    )
    fig.update_layout(xaxis_tickangle=-45, height=500)

    mo.md("## Top Hitters by FGPts (2024)")
    mo.ui.plotly(fig)
    return


@app.cell
def _(con, mo, px):
    # Top 20 pitchers by FGPts
    top_pitchers = con.execute("""
        SELECT Name, Team, IP, SO, ERA,
               (IP * 7.4 + SO * 2.0 + H * -2.6 + BB * -3.0 + HBP * -3.0 +
                HR * -12.3 + SV * 5.0 + HLD * 4.0) as fgpts
        FROM fg_pitching
        WHERE Season = 2024 AND IP >= 100
        ORDER BY fgpts DESC
        LIMIT 20
    """).fetchdf()

    fig = px.bar(
        top_pitchers, x="Name", y="fgpts",
        color="fgpts", color_continuous_scale="Blues",
        title="Top 20 Pitchers by FGPts (2024, 100+ IP)",
        labels={"fgpts": "FanGraphs Points", "Name": ""},
    )
    fig.update_layout(xaxis_tickangle=-45, height=500)

    mo.md("## Top Pitchers by FGPts (2024)")
    mo.ui.plotly(fig)
    return


@app.cell
def _(con, mo):
    # Pitcher selector for movement profile
    _pitchers = con.execute("""
        SELECT DISTINCT player_name, pitcher,
               COUNT(*) as pitches
        FROM statcast_pitches
        WHERE pitch_type IS NOT NULL
        GROUP BY player_name, pitcher
        HAVING COUNT(*) >= 500
        ORDER BY pitches DESC
    """).fetchdf()
    _options = {row["player_name"]: str(row["pitcher"]) for _, row in _pitchers.iterrows()}
    pitcher_select = mo.ui.dropdown(
        options=_options,
        value=str(_pitchers.iloc[0]["pitcher"]),
        label="Select Pitcher",
    )
    mo.md("## Movement Profile (Induced Break)")
    pitcher_select
    return (pitcher_select,)


@app.cell
def _(con, go, mo, pitcher_select):
    import numpy as np

    _pid = int(pitcher_select.value)

    # Get pitch-level movement data for selected pitcher
    _pitches = con.execute(f"""
        SELECT pitch_type, pfx_x * 12 as h_break, pfx_z * 12 as v_break,
               release_speed, player_name
        FROM statcast_pitches
        WHERE pitcher = {_pid}
        AND pitch_type IS NOT NULL
        AND pfx_x IS NOT NULL AND pfx_z IS NOT NULL
    """).fetchdf()

    _pname = _pitches["player_name"].iloc[0] if len(_pitches) > 0 else "Unknown"

    # MLB averages by pitch type for comparison
    _mlb_avg = con.execute("""
        SELECT pitch_type,
               AVG(pfx_x * 12) as avg_h, AVG(pfx_z * 12) as avg_v,
               AVG(release_speed) as avg_velo
        FROM statcast_pitches
        WHERE pitch_type IS NOT NULL AND pfx_x IS NOT NULL
        GROUP BY pitch_type
    """).fetchdf().set_index("pitch_type")

    # Pitch type colors matching Statcast
    _colors = {
        "FF": "#D4474E", "SI": "#F28C38", "FC": "#E88DA0", "CH": "#4CAF50",
        "SL": "#F0C73B", "CU": "#5BBFDF", "ST": "#E040C0", "SV": "#7B1FA2",
        "KC": "#E91E63", "FS": "#26C6DA", "KN": "#795548",
    }

    fig = go.Figure()

    # Concentric circles at 6", 12", 18", 24"
    for r in [6, 12, 18, 24]:
        _theta = np.linspace(0, 2 * np.pi, 100)
        fig.add_trace(go.Scatter(
            x=r * np.cos(_theta), y=r * np.sin(_theta),
            mode="lines", line=dict(color="#B0BEC5", width=1, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_annotation(x=0, y=r, text=f'{r}"', showarrow=False,
                          font=dict(size=10, color="#90A4AE"), yshift=8)

    # Axis lines
    fig.add_hline(y=0, line=dict(color="#B0BEC5", width=1), opacity=0.5)
    fig.add_vline(x=0, line=dict(color="#B0BEC5", width=1), opacity=0.5)

    # MLB average ellipses (background)
    for pt in _pitches["pitch_type"].unique():
        if pt in _mlb_avg.index:
            _avg = _mlb_avg.loc[pt]
            _theta = np.linspace(0, 2 * np.pi, 60)
            _c = _colors.get(pt, "#999999")
            fig.add_trace(go.Scatter(
                x=_avg["avg_h"] + 3.5 * np.cos(_theta),
                y=_avg["avg_v"] + 3.5 * np.sin(_theta),
                mode="lines", line=dict(color=_c, width=1.5, dash="dash"),
                fill="toself", fillcolor=_c, opacity=0.08,
                showlegend=False, hoverinfo="skip",
            ))

    # Pitch dots
    for pt in _pitches["pitch_type"].unique():
        _subset = _pitches[_pitches["pitch_type"] == pt]
        _c = _colors.get(pt, "#999999")
        _avg_velo = _subset["release_speed"].mean()
        _usage = len(_subset) / len(_pitches) * 100
        fig.add_trace(go.Scatter(
            x=_subset["h_break"], y=_subset["v_break"],
            mode="markers",
            marker=dict(size=6, color=_c, opacity=0.7, line=dict(width=0.5, color="white")),
            name=f"{pt} ({_usage:.0f}%, {_avg_velo:.1f} mph)",
            hovertemplate=f"{pt}<br>H-Break: %{{x:.1f}}\"<br>V-Break: %{{y:.1f}}\"<br>Velo: {_avg_velo:.1f}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=f"{_pname} - 2024 Movement Profile (Induced Break)", font=dict(size=18)),
        xaxis=dict(
            title="Horizontal Break (in.)",
            range=[-28, 28], dtick=6, zeroline=False,
            gridcolor="rgba(0,0,0,0)",
        ),
        yaxis=dict(
            title="Induced Vertical Break (in.)",
            range=[-28, 28], dtick=6, zeroline=False,
            gridcolor="rgba(0,0,0,0)",
            scaleanchor="x", scaleratio=1,
        ),
        height=700, width=700,
        plot_bgcolor="#F5F8FA",
        paper_bgcolor="white",
        legend=dict(
            orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5,
            font=dict(size=11),
        ),
        annotations=[
            dict(x=-26, y=14, text="MORE<br>RISE<br>▲", showarrow=False,
                 font=dict(size=9, color="#78909C"), xanchor="left"),
            dict(x=-26, y=-14, text="▼<br>MORE<br>DROP", showarrow=False,
                 font=dict(size=9, color="#78909C"), xanchor="left"),
            dict(x=-20, y=27, text="◄ 1B side", showarrow=False,
                 font=dict(size=9, color="#78909C")),
            dict(x=20, y=27, text="3B side ►", showarrow=False,
                 font=dict(size=9, color="#78909C")),
            dict(x=20, y=-26, text="MLB AVG = dashed ellipse", showarrow=False,
                 font=dict(size=8, color="#B0BEC5")),
        ],
    )

    mo.ui.plotly(fig)
    return


@app.cell
def _(con, mo, px):
    # Exit velocity distribution
    ev_data = con.execute("""
        SELECT launch_speed, launch_angle, events
        FROM statcast_pitches
        WHERE launch_speed IS NOT NULL
        AND launch_speed >= 50
        AND events IS NOT NULL
    """).fetchdf()

    fig = px.scatter(
        ev_data.sample(n=min(20000, len(ev_data)), random_state=42),
        x="launch_angle", y="launch_speed", color="events",
        title="Exit Velocity vs Launch Angle (sample of 20K batted balls)",
        labels={"launch_angle": "Launch Angle", "launch_speed": "Exit Velocity (mph)"},
        opacity=0.3,
        height=600,
    )

    mo.md("## Exit Velocity vs Launch Angle")
    mo.ui.plotly(fig)
    return


@app.cell
def _(con, mo, px):
    # Ottoneu value comparison: most expensive players
    ottoneu = con.execute("""
        SELECT
            f.Name,
            f."Position(s)" as Positions,
            f."MLB Org" as Team,
            CAST(REPLACE(f."Avg Salary", '$', '') AS FLOAT) as fgpts_salary,
            CAST(REPLACE(s."Avg Salary", '$', '') AS FLOAT) as sabr_salary
        FROM ottoneu_fgpts_values f
        JOIN ottoneu_sabr_values s ON f.OttoneuID = s.OttoneuID
        WHERE CAST(REPLACE(f."Avg Salary", '$', '') AS FLOAT) > 0
        ORDER BY fgpts_salary DESC
        LIMIT 30
    """).fetchdf()

    fig = px.scatter(
        ottoneu, x="fgpts_salary", y="sabr_salary",
        text="Name", color="Positions",
        title="Ottoneu FGPts vs SABR Salary (Top 30 by FGPts)",
        labels={"fgpts_salary": "FGPts Avg Salary ($)", "sabr_salary": "SABR Avg Salary ($)"},
        height=600,
    )
    fig.update_traces(textposition="top center", textfont_size=9)

    mo.md("## Ottoneu FGPts vs SABR Salaries")
    mo.ui.plotly(fig)
    return


@app.cell
def _(con, mo):
    # Custom SQL query cell
    sql_input = mo.ui.text_area(
        value="SELECT Name, Team, HR, SB, AVG, OBP, SLG\nFROM fg_batting\nWHERE Season = 2024 AND PA >= 500\nORDER BY HR DESC\nLIMIT 20",
        label="Custom SQL Query",
        full_width=True,
    )
    mo.md("## Custom SQL Query\n\nRun any query against the database.")
    sql_input
    return (sql_input,)


@app.cell
def _(con, mo, sql_input):
    if sql_input.value.strip():
        try:
            result = con.execute(sql_input.value).fetchdf()
            mo.md(f"**{len(result)} rows returned**")
            mo.ui.table(result)
        except Exception as e:
            mo.md(f"**Error:** {e}")
    return


if __name__ == "__main__":
    app.run()
