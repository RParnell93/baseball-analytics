import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import pandas as pd
    import plotly.express as px

    mo.md("""# Ottoneu Value Finder

    Find undervalued and overvalued players by comparing projected FGPts/SABR production
    to current Ottoneu market salaries.""")
    return duckdb, mo, pd, px


@app.cell
def _(duckdb, mo, pd):
    con = duckdb.connect("data/database/baseball.duckdb", read_only=True)

    format_picker = mo.ui.dropdown(
        options={"FGPts": "fgpts", "SABR": "sabr"},
        value="fgpts",
        label="Scoring Format",
    )
    min_pa = mo.ui.slider(100, 600, value=300, step=50, label="Min PA (2024)")

    mo.md("## Settings")
    mo.hstack([format_picker, min_pa])
    return con, format_picker, min_pa


@app.cell
def _(con, format_picker, min_pa, mo, pd, px):
    fmt = format_picker.value

    # Calculate FGPts for all qualified batters
    batting = con.execute(f"""
        WITH scored AS (
            SELECT
                b.Name,
                b.Team,
                b.PA,
                b.HR,
                b.SB,
                b.AVG,
                ROUND(b.AB * -1.0 + b.H * 5.6 + b."2B" * 2.9 + b."3B" * 5.7 + b.HR * 9.4 +
                      b.BB * 3.0 + b.HBP * 3.0 + b.SB * 1.9 + b.CS * -2.8, 1) as points,
                b.IDfg
            FROM fg_batting b
            WHERE b.Season = 2024
            AND b.PA >= {min_pa.value}
        )
        SELECT
            s.*,
            ROUND(s.points / s.PA * 600, 1) as points_per_600pa,
            o."Avg Salary" as ottoneu_salary,
            o."Position(s)" as positions
        FROM scored s
        LEFT JOIN ottoneu_{fmt}_values o ON CAST(s.IDfg AS VARCHAR) = CAST(o."FG MajorLeagueID" AS VARCHAR)
        WHERE o."Avg Salary" IS NOT NULL
        ORDER BY points DESC
    """).fetchdf()

    # Clean salary column
    batting["salary_num"] = batting["ottoneu_salary"].str.replace("$", "").astype(float)

    # Calculate value ratio (points per dollar)
    batting["points_per_dollar"] = (batting["points"] / batting["salary_num"].replace(0, 0.01)).round(1)

    mo.md(f"## Batting - {fmt.upper()} Format\n\n**{len(batting)} qualified batters**")
    return (batting,)


@app.cell
def _(batting, mo, px):
    # Scatter: points vs salary
    fig = px.scatter(
        batting,
        x="salary_num",
        y="points",
        text="Name",
        color="positions",
        title="2024 FGPts Production vs Current Ottoneu Salary",
        labels={"salary_num": "Ottoneu Avg Salary ($)", "points": "2024 Points"},
        height=600,
        hover_data=["Team", "PA", "HR", "SB", "AVG"],
    )
    fig.update_traces(textposition="top center", textfont_size=8)

    mo.ui.plotly(fig)
    return


@app.cell
def _(batting, mo):
    # Best values (highest points per dollar)
    best = batting.nlargest(20, "points_per_dollar")[
        ["Name", "Team", "positions", "PA", "points", "ottoneu_salary", "points_per_dollar"]
    ]
    mo.md("## Best Values (Highest Points per Dollar)")
    mo.ui.table(best)
    return


@app.cell
def _(batting, mo):
    # Most overvalued (lowest points per dollar among expensive players)
    expensive = batting[batting["salary_num"] >= 5].nsmallest(15, "points_per_dollar")[
        ["Name", "Team", "positions", "PA", "points", "ottoneu_salary", "points_per_dollar"]
    ]
    mo.md("## Most Overvalued ($5+ salary, lowest points per dollar)")
    mo.ui.table(expensive)
    return


@app.cell
def _(con, format_picker, mo, pd, px):
    fmt = format_picker.value

    # Pitching analysis
    if fmt == "fgpts":
        pts_formula = "ROUND(IP * 7.4 + SO * 2.0 + H * -2.6 + BB * -3.0 + HBP * -3.0 + HR * -12.3 + SV * 5.0 + HLD * 4.0, 1)"
    else:
        pts_formula = "ROUND(IP * 5.0 + SO * 2.0 + BB * -3.0 + HBP * -3.0 + HR * -13.0 + SV * 5.0 + HLD * 4.0, 1)"

    pitching = con.execute(f"""
        WITH scored AS (
            SELECT
                p.Name,
                p.Team,
                p.IP,
                p.SO,
                p.ERA,
                {pts_formula} as points,
                p.IDfg
            FROM fg_pitching p
            WHERE p.Season = 2024
            AND p.IP >= 50
        )
        SELECT
            s.*,
            ROUND(s.points / GREATEST(s.IP, 1) * 180, 1) as points_per_180ip,
            o."Avg Salary" as ottoneu_salary,
            o."Position(s)" as positions
        FROM scored s
        LEFT JOIN ottoneu_{fmt}_values o ON CAST(s.IDfg AS VARCHAR) = CAST(o."FG MajorLeagueID" AS VARCHAR)
        WHERE o."Avg Salary" IS NOT NULL
        ORDER BY points DESC
    """).fetchdf()

    pitching["salary_num"] = pitching["ottoneu_salary"].str.replace("$", "").astype(float)
    pitching["points_per_dollar"] = (pitching["points"] / pitching["salary_num"].replace(0, 0.01)).round(1)

    mo.md(f"## Pitching - {fmt.upper()} Format\n\n**{len(pitching)} qualified pitchers (50+ IP)**")

    fig = px.scatter(
        pitching,
        x="salary_num",
        y="points",
        text="Name",
        title=f"2024 {fmt.upper()} Pitching Production vs Ottoneu Salary",
        labels={"salary_num": "Ottoneu Avg Salary ($)", "points": "2024 Points"},
        height=600,
        hover_data=["Team", "IP", "SO", "ERA"],
    )
    fig.update_traces(textposition="top center", textfont_size=8)
    mo.ui.plotly(fig)
    return


if __name__ == "__main__":
    app.run()
