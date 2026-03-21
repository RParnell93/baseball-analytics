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
    import plotly.express as px
    import plotly.graph_objects as go

    mo.md("""# Ottoneu Value Finder

    Find undervalued and overvalued players by comparing projected FGPts/SABR production
    to current Ottoneu market salaries.""")
    return duckdb, go, mo, np, os, pd, px


@app.cell
def _(duckdb, mo, os):
    _password = os.environ.get("MOTHERDUCK_TOKEN")
    con = duckdb.connect("md:baseball", config={"motherduck_token": _password})

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


# ── Surplus Value Analysis ──────────────────────────────────────────────────
# Gap: No third-party Ottoneu analytics tools exist.
# This estimates dollar values and identifies the biggest steals/overpays.

@app.cell
def _(batting, go, mo, np, pd):
    DARK = {
        "bg": "#0e1117", "card": "#1a1a2e", "text": "#e0e0e0",
        "muted": "#8892a0", "accent": "#FF6B35", "green": "#2ECC71",
        "red": "#E74C3C", "gold": "#F1C40F", "grid": "#2d2d44",
    }

    if len(batting) == 0:
        mo.md("## Surplus Value Analysis\n*No batting data available.*")
    else:
        _df = batting.copy()

        # Estimate dollar value: scale linearly from top producer = ~$45
        _max_pts = _df["points"].max()
        _rate = 45.0 / _max_pts if _max_pts > 0 else 0
        _df["est_value"] = (_df["points"] * _rate).round(1)
        _df["surplus"] = (_df["est_value"] - _df["salary_num"]).round(1)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=_df["salary_num"], y=_df["points"],
            mode="markers",
            marker=dict(
                size=10,
                color=_df["surplus"],
                colorscale=[[0, DARK["red"]], [0.5, DARK["muted"]], [1, DARK["green"]]],
                cmin=-20, cmax=20,
                colorbar=dict(title="Surplus $", tickprefix="$", len=0.6),
                line=dict(width=0.5, color="white"),
                opacity=0.8,
            ),
            text=_df.apply(
                lambda r: r["Name"] if abs(r["surplus"]) > 10 else "", axis=1
            ),
            textposition="top center",
            textfont=dict(size=8, color=DARK["text"]),
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                "Points: %{y:.0f}<br>"
                "Salary: $%{x:.1f}<br>"
                "Est Value: $%{customdata[2]:.1f}<br>"
                "Surplus: $%{customdata[3]:+.1f}<extra></extra>"
            ),
            customdata=list(zip(
                _df["Name"], _df["Team"],
                _df["est_value"], _df["surplus"],
            )),
        ))

        # Fair value line
        _x_max = _df["salary_num"].max() * 1.1
        fig.add_trace(go.Scatter(
            x=[0, _x_max], y=[0, _x_max / _rate],
            mode="lines",
            line=dict(color=DARK["gold"], width=1.5, dash="dash"),
            name="Fair Value", showlegend=True,
        ))

        fig.update_layout(
            paper_bgcolor=DARK["bg"], plot_bgcolor=DARK["card"],
            font=dict(family="Helvetica Neue, Arial", color=DARK["text"]),
            title=dict(
                text="Surplus Value: Who's a Steal?<br>"
                     "<sub>Above line = bargain | Below line = overpay</sub>",
                font=dict(size=16, color=DARK["text"]),
                x=0.5, xanchor="center",
            ),
            xaxis=dict(title="Ottoneu Avg Salary ($)", gridcolor=DARK["grid"]),
            yaxis=dict(title="2024 Points", gridcolor=DARK["grid"]),
            height=650,
            margin=dict(t=80, b=60, l=60, r=40),
            legend=dict(
                orientation="h", yanchor="top", y=-0.08,
                xanchor="center", x=0.5,
            ),
            annotations=[
                dict(x=0.98, y=0.02, xref="paper", yref="paper",
                     text="@sabrmagician", showarrow=False,
                     font=dict(size=9, color=DARK["muted"])),
            ],
        )

        mo.md("## Surplus Value Analysis\n"
               "*No third-party Ottoneu analytics exist. "
               "Green = undervalued, red = overvalued.*")
        mo.ui.plotly(fig)
    return


# ── Position Scarcity ──────────────────────────────────────────────────────
# Gap: Nobody produces SABR Points format content.
# This shows where positional scarcity creates Ottoneu roster value.

@app.cell
def _(con, format_picker, go, mo, pd):
    fmt = format_picker.value

    DARK = {
        "bg": "#0e1117", "card": "#1a1a2e", "text": "#e0e0e0",
        "muted": "#8892a0", "accent": "#FF6B35", "grid": "#2d2d44",
    }

    _pos_data = con.execute(f"""
        WITH scored AS (
            SELECT
                b.Name, b.Team, b.PA,
                ROUND(b.AB * -1.0 + b.H * 5.6 + b."2B" * 2.9 + b."3B" * 5.7 +
                      b.HR * 9.4 + b.BB * 3.0 + b.HBP * 3.0 + b.SB * 1.9 +
                      b.CS * -2.8, 1) as pts,
                ROUND((b.AB * -1.0 + b.H * 5.6 + b."2B" * 2.9 + b."3B" * 5.7 +
                       b.HR * 9.4 + b.BB * 3.0 + b.HBP * 3.0 + b.SB * 1.9 +
                       b.CS * -2.8) / b.PA * 600, 1) as pts_600,
                o."Position(s)" as positions
            FROM fg_batting b
            LEFT JOIN ottoneu_{fmt}_values o
                ON CAST(b.IDfg AS VARCHAR) = CAST(o."FG MajorLeagueID" AS VARCHAR)
            WHERE b.Season = 2024 AND b.PA >= 200
            AND o."Position(s)" IS NOT NULL
        )
        SELECT * FROM scored
    """).fetchdf()

    if len(_pos_data) == 0:
        mo.md("## Position Scarcity\n*No position data available.*")
    else:
        _pos_data["primary_pos"] = _pos_data["positions"].str.split("/").str[0]
        _pos_order = ["C", "1B", "2B", "3B", "SS", "OF", "DH", "Util"]
        _pos_data = _pos_data[_pos_data["primary_pos"].isin(_pos_order)]

        _pos_colors = {
            "C": "#E74C3C", "1B": "#FF6B35", "2B": "#F1C40F",
            "3B": "#2ECC71", "SS": "#4ECDC4", "OF": "#3498DB",
            "DH": "#9B59B6", "Util": "#8892a0",
        }

        fig = go.Figure()
        for pos in _pos_order:
            _sub = _pos_data[_pos_data["primary_pos"] == pos]
            if len(_sub) > 0:
                fig.add_trace(go.Box(
                    y=_sub["pts_600"],
                    name=f"{pos} ({len(_sub)})",
                    marker=dict(color=_pos_colors.get(pos, "#8892a0"), opacity=0.6),
                    line=dict(color=_pos_colors.get(pos, "#8892a0")),
                    boxmean=True,
                ))

        fig.update_layout(
            paper_bgcolor=DARK["bg"], plot_bgcolor=DARK["card"],
            font=dict(family="Helvetica Neue, Arial", color=DARK["text"]),
            title=dict(
                text=f"{fmt.upper()} Points by Position - Where's the Scarcity?",
                font=dict(size=16, color=DARK["text"]),
                x=0.5, xanchor="center",
            ),
            xaxis=dict(gridcolor=DARK["grid"]),
            yaxis=dict(
                title="Points per 600 PA",
                gridcolor=DARK["grid"],
                zerolinecolor=DARK["grid"],
            ),
            height=550,
            showlegend=False,
            margin=dict(t=80, b=80, l=60, r=40),
            annotations=[
                dict(x=0.98, y=0.02, xref="paper", yref="paper",
                     text="@sabrmagician", showarrow=False,
                     font=dict(size=9, color=DARK["muted"])),
                dict(x=0.5, y=-0.12, xref="paper", yref="paper",
                     text=("200+ PA, 2024. Diamond = mean. "
                           "Scarce positions (C, SS, 2B) produce fewer points, "
                           "driving Ottoneu value."),
                     showarrow=False,
                     font=dict(size=9, color=DARK["muted"]),
                     xanchor="center"),
            ],
        )

        mo.md("## Position Scarcity\n"
               "*Nobody produces SABR Points content. This shows where positional "
               "scarcity drives Ottoneu roster construction.*")
        mo.ui.plotly(fig)
    return


if __name__ == "__main__":
    app.run()
