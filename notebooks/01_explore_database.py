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
    from dotenv import load_dotenv

    load_dotenv()

    mo.md("# Baseball Analytics - Database Explorer\n\nExplore the data loaded into our DuckDB database.")
    return duckdb, go, mo, os, pd, px


@app.cell
def _(duckdb, mo, os, pd):
    # Connect to MotherDuck if token is set, otherwise fall back to local DuckDB
    if os.environ.get("MOTHERDUCK_TOKEN"):
        con = duckdb.connect("md:baseball")
    else:
        con = duckdb.connect("data/database/baseball.duckdb", read_only=True)

    # Show all tables
    tables = con.execute("SHOW TABLES").fetchdf()
    table_info = []
    for t in tables["name"]:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = len(con.execute(f"SELECT * FROM {t} LIMIT 0").description)
        table_info.append({"Table": t, "Rows": f"{count:,}", "Columns": cols})

    mo.md(f"""## Database Summary\n\n{pd.DataFrame(table_info).to_markdown(index=False)}""")
    return (con,)


@app.cell
def _(con, mo, pd, px):
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
def _(con, mo, px):
    # Pitch type distribution
    pitch_dist = con.execute("""
        SELECT pitch_type, COUNT(*) as count,
               ROUND(AVG(release_speed), 1) as avg_velo,
               ROUND(AVG(pfx_x * 12), 1) as avg_h_break_in,
               ROUND(AVG(pfx_z * 12), 1) as avg_v_break_in
        FROM statcast_pitches
        WHERE pitch_type IS NOT NULL
        GROUP BY pitch_type
        ORDER BY count DESC
    """).fetchdf()

    fig = px.bar(
        pitch_dist, x="pitch_type", y="count",
        color="avg_velo", color_continuous_scale="RdYlBu_r",
        title="2024 Pitch Type Distribution (colored by avg velocity)",
        labels={"pitch_type": "Pitch Type", "count": "Count", "avg_velo": "Avg Velo"},
        hover_data=["avg_velo", "avg_h_break_in", "avg_v_break_in"],
    )
    fig.update_layout(height=500)

    mo.md("## Pitch Type Distribution (2024)")
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
