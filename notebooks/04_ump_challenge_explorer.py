import marimo

__generated_with = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import json
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    from scipy.stats import gaussian_kde
    from pathlib import Path

    mo.md("# ABS Challenge Explorer\n\nInteractive umpire challenge maps for Spring Training 2026.")
    return Path, go, json, mo, np, pd, gaussian_kde


@app.cell
def _(Path, json, pd):
    # Load challenge data
    challenge_path = Path(__file__).parent.parent / "output" / "abs" / "spring_training_challenges.json"
    if not challenge_path.exists():
        challenge_path = Path("output/abs/spring_training_challenges.json")

    with open(challenge_path) as f:
        raw = json.load(f)

    df = pd.DataFrame(raw)
    df["date"] = pd.to_datetime(df["date"])
    df["impact_score"] = df["impact"].apply(lambda x: x.get("impact_score", 0) if isinstance(x, dict) else 0)
    df["impact_label"] = df["impact"].apply(lambda x: x.get("impact_label", "") if isinstance(x, dict) else "")
    return (df,)


@app.cell
def _(df, mo):
    # Build filter options
    umpires = sorted(df["umpire"].unique().tolist())
    teams = sorted(set(df["away"].unique().tolist() + df["home"].unique().tolist()))
    results = ["All", "overturned", "upheld"]
    original_calls = ["All"] + sorted(df["original_call"].unique().tolist())

    umpire_dropdown = mo.ui.dropdown(
        options=dict(zip(["All Umpires"] + umpires, ["All"] + umpires)),
        value="All Umpires",
        label="Umpire",
    )
    team_dropdown = mo.ui.dropdown(
        options=dict(zip(["All Teams"] + teams, ["All"] + teams)),
        value="All Teams",
        label="Team",
    )

    mo.hstack([umpire_dropdown, team_dropdown], gap=1)
    return team_dropdown, umpire_dropdown


@app.cell
def _(df, team_dropdown, umpire_dropdown):
    # Apply filters
    filtered = df.copy()

    if umpire_dropdown.value != "All":
        filtered = filtered[filtered["umpire"] == umpire_dropdown.value]

    if team_dropdown.value != "All":
        filtered = filtered[filtered["challenge_team"] == team_dropdown.value]

    return (filtered,)


@app.cell
def _(filtered, gaussian_kde, go, mo, np):
    # Build the challenge map
    valid = filtered.dropna(subset=["pX", "pZ"])

    if len(valid) == 0:
        mo.output.replace(mo.md("**No challenges match the current filters.**"))
    else:
        n_total = len(valid)
        n_ot = (valid["result"] == "overturned").sum()
        n_up = (valid["result"] == "upheld").sum()
        ot_pct = n_ot / max(n_total, 1) * 100

        # Title
        ump_label = filtered["umpire"].iloc[0] if filtered["umpire"].nunique() == 1 else "All Umpires"
        team_label = filtered["challenge_team"].iloc[0] if filtered["challenge_team"].nunique() == 1 else "All Teams"

        # Calculate distance from zone edge for each pitch
        plate_half_calc = 0.7083
        def zone_distance(row):
            px, pz = abs(row["pX"]), row["pZ"]
            sz_t = row.get("sz_top", 3.4)
            sz_b = row.get("sz_bottom", 1.6)
            # Distance outside zone on each axis (0 if inside)
            dx = max(0, px - plate_half_calc)
            dz_above = max(0, pz - sz_t)
            dz_below = max(0, sz_b - pz)
            dz = max(dz_above, dz_below)
            if dx > 0 or dz > 0:
                # Outside zone - Euclidean distance to nearest edge
                return np.sqrt(dx**2 + dz**2)
            else:
                # Inside zone - min distance to any edge (negative = inside)
                return -min(plate_half_calc - px, px + plate_half_calc, pz - sz_b, sz_t - pz)

        valid = valid.copy()
        valid["zone_dist"] = valid.apply(zone_distance, axis=1)
        valid["zone_dist_label"] = valid.apply(
            lambda r: f"{abs(r['zone_dist']) * 12:.1f} in outside zone" if r["zone_dist"] > 0
            else f"{abs(r['zone_dist']) * 12:.1f} in inside zone", axis=1
        )

        # KDE heatmap background
        x = valid["pX"].values
        z = valid["pZ"].values

        xmin, xmax = -4.0, 4.0
        zmin, zmax = 0.0, 4.5
        xx, zz = np.mgrid[xmin:xmax:200j, zmin:zmax:200j]
        positions = np.vstack([xx.ravel(), zz.ravel()])

        try:
            kernel = gaussian_kde(np.vstack([x, z]), bw_method=0.3)
            density = np.reshape(kernel(positions), xx.shape)
        except Exception:
            density = np.zeros(xx.shape)

        # Colors
        overturned_color = "#ff6b6b"
        upheld_color = "#51cf66"
        bg_color = "#1a1b2e"

        fig = go.Figure()

        # KDE contour - challenge density (proxy for established zone)
        fig.add_trace(go.Contour(
            x=np.linspace(xmin, xmax, 200),
            y=np.linspace(zmin, zmax, 200),
            z=density.T,
            colorscale=[
                [0, "rgba(26,27,46,0)"],
                [0.15, "rgba(80,0,60,0.25)"],
                [0.3, "rgba(120,0,80,0.4)"],
                [0.5, "rgba(160,0,100,0.55)"],
                [0.7, "rgba(200,20,120,0.65)"],
                [0.85, "rgba(230,40,140,0.75)"],
                [1.0, "rgba(255,80,180,0.85)"],
            ],
            contours=dict(
                coloring="fill",
                showlines=True,
                showlabels=False,
            ),
            line=dict(width=0.5, color="rgba(255,255,255,0.1)"),
            showscale=True,
            colorbar=dict(
                title="",
                orientation="h",
                y=-0.08,
                yanchor="top",
                x=0.25,
                xanchor="center",
                len=0.35,
                thickness=12,
                tickvals=[],
                ticktext=[],
            ),
            hoverinfo="skip",
            showlegend=False,
        ))

        # Rule book strike zone
        sz_top = valid["sz_top"].mean() if "sz_top" in valid.columns else 3.4
        sz_bot = valid["sz_bottom"].mean() if "sz_bottom" in valid.columns else 1.6
        plate_half = 0.7083  # 17 inches / 2 in feet

        # Strike zone border
        for x0, x1, y0, y1 in [
            (-plate_half, plate_half, sz_bot, sz_bot),
            (-plate_half, plate_half, sz_top, sz_top),
            (-plate_half, -plate_half, sz_bot, sz_top),
            (plate_half, plate_half, sz_bot, sz_top),
        ]:
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode="lines", line=dict(color="rgba(255,255,255,0.5)", width=2),
                showlegend=False, hoverinfo="skip",
            ))

        # Inner zone lines (thirds)
        third_h = (sz_top - sz_bot) / 3
        third_w = plate_half * 2 / 3
        for i in range(1, 3):
            fig.add_trace(go.Scatter(
                x=[-plate_half, plate_half],
                y=[sz_bot + third_h * i, sz_bot + third_h * i],
                mode="lines", line=dict(color="rgba(255,255,255,0.15)", width=0.5, dash="dot"),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=[-plate_half + third_w * i, -plate_half + third_w * i],
                y=[sz_bot, sz_top],
                mode="lines", line=dict(color="rgba(255,255,255,0.15)", width=0.5, dash="dot"),
                showlegend=False, hoverinfo="skip",
            ))

        # Home plate
        plate_y = 0.5
        fig.add_trace(go.Scatter(
            x=[-plate_half, -plate_half, 0, plate_half, plate_half, -plate_half],
            y=[plate_y, plate_y - 0.15, plate_y - 0.3, plate_y - 0.15, plate_y, plate_y],
            mode="lines", line=dict(color="rgba(255,255,255,0.3)", width=1),
            fill="toself", fillcolor="rgba(255,255,255,0.05)",
            showlegend=False, hoverinfo="skip",
        ))

        # Challenge dots - overturned
        ot = valid[valid["result"] == "overturned"]
        if len(ot) > 0:
            fig.add_trace(go.Scatter(
                x=ot["pX"], y=ot["pZ"],
                mode="markers+text",
                marker=dict(size=18, color=overturned_color, opacity=0.85,
                            line=dict(width=1.5, color="white")),
                text=ot["challenge_team"],
                textfont=dict(size=7, color="white"),
                textposition="middle center",
                name=f"Overturned ({n_ot})",
                legendgroup="overturned",
                customdata=np.stack([
                    ot["umpire"], ot["batter"], ot["pitcher"],
                    ot["pitch_name"], ot["speed"].round(1),
                    ot["original_call"], ot["impact_score"].round(0),
                    ot["date"].dt.strftime("%m/%d"),
                    ot["zone_dist_label"],
                ], axis=-1),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[7]} | %{customdata[5]}<br>"
                    "%{customdata[1]} vs %{customdata[2]}<br>"
                    "%{customdata[3]} @ %{customdata[4]} mph<br>"
                    "Impact: %{customdata[6]}<br>"
                    "<b>%{customdata[8]}</b><br>"
                    "pX: %{x:.2f} | pZ: %{y:.2f}"
                    "<extra></extra>"
                ),
            ))

        # Challenge dots - upheld
        up = valid[valid["result"] == "upheld"]
        if len(up) > 0:
            fig.add_trace(go.Scatter(
                x=up["pX"], y=up["pZ"],
                mode="markers+text",
                marker=dict(size=18, color=upheld_color, opacity=0.85,
                            line=dict(width=1.5, color="white")),
                text=up["challenge_team"],
                textfont=dict(size=7, color="white"),
                textposition="middle center",
                name=f"Upheld ({n_up})",
                legendgroup="upheld",
                customdata=np.stack([
                    up["umpire"], up["batter"], up["pitcher"],
                    up["pitch_name"], up["speed"].round(1),
                    up["original_call"], up["impact_score"].round(0),
                    up["date"].dt.strftime("%m/%d"),
                    up["zone_dist_label"],
                ], axis=-1),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[7]} | %{customdata[5]}<br>"
                    "%{customdata[1]} vs %{customdata[2]}<br>"
                    "%{customdata[3]} @ %{customdata[4]} mph<br>"
                    "Impact: %{customdata[6]}<br>"
                    "<b>%{customdata[8]}</b><br>"
                    "pX: %{x:.2f} | pZ: %{y:.2f}"
                    "<extra></extra>"
                ),
            ))

        fig.update_layout(
            title=dict(
                text=(
                    f"<b>ABS Challenge Map: {ump_label}</b><br>"
                    f"<span style='font-size:13px;color:#aaa'>"
                    f"Spring Training 2026 | {team_label} | {n_total} challenges | "
                    f"{n_ot} overturned ({ot_pct:.0f}%) | {n_up} upheld ({100-ot_pct:.0f}%)</span>"
                ),
                font=dict(size=18, color="white"),
                x=0.5,
            ),
            xaxis=dict(
                title="Horizontal Location (ft from center)",
                range=[-2, 2],
                zeroline=False,
                gridcolor="rgba(255,255,255,0.05)",
                color="#aaa",
            ),
            yaxis=dict(
                title="Vertical Location (ft)",
                range=[0, 4.5],
                zeroline=False,
                gridcolor="rgba(255,255,255,0.05)",
                color="#aaa",
                scaleanchor="x",
            ),
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color="white"),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.12, xanchor="right", x=0.98,
                font=dict(size=14),
                itemsizing="constant",
                itemclick="toggle",
                itemdoubleclick="toggleothers",
            ),
            height=750,
            margin=dict(t=100, b=120),
        )

        # Colorbar text labels
        fig.add_annotation(x=0.08, y=-0.1, xref="paper", yref="paper",
                           text="No strikes", showarrow=False,
                           font=dict(size=10, color="#888"))
        fig.add_annotation(x=0.25, y=-0.1, xref="paper", yref="paper",
                           text="Fringe", showarrow=False,
                           font=dict(size=10, color="#888"))
        fig.add_annotation(x=0.42, y=-0.1, xref="paper", yref="paper",
                           text="Core zone", showarrow=False,
                           font=dict(size=10, color="#888"))

        # Annotations
        fig.add_annotation(x=-1.5, y=4.3, text="Ump's left", showarrow=False,
                           font=dict(size=10, color="#666"))
        fig.add_annotation(x=1.5, y=4.3, text="Ump's right", showarrow=False,
                           font=dict(size=10, color="#666"))
        fig.add_annotation(x=0, y=0.1, text="Umpire's view (behind catcher)", showarrow=False,
                           font=dict(size=10, color="#666"))

        mo.output.replace(fig)
    return


@app.cell
def _(filtered, mo):
    # Summary stats table
    if len(filtered) == 0:
        mo.output.replace(mo.md(""))
    else:
        _n = len(filtered)
        _n_ot = (filtered["result"] == "overturned").sum()
        _avg_impact = filtered["impact_score"].mean()

        _by_call = filtered.groupby("original_call").agg(
            count=("result", "size"),
            overturned=("result", lambda x: (x == "overturned").sum()),
        ).reset_index()
        _by_call["overturn_rate"] = (_by_call["overturned"] / _by_call["count"] * 100).round(1)
        _by_call = _by_call.sort_values("count", ascending=False)

        mo.output.replace(mo.vstack([
            mo.md(f"### Summary: {_n} challenges | {_n_ot} overturned ({_n_ot/max(_n,1)*100:.0f}%) | Avg Impact: {_avg_impact:.1f}"),
            mo.ui.table(_by_call.rename(columns={
                "original_call": "Original Call",
                "count": "Challenges",
                "overturned": "Overturned",
                "overturn_rate": "Overturn %",
            })),
        ]))
    return


@app.cell
def _(filtered, go, mo):
    # Top umpires by challenge count
    if len(filtered) < 5:
        mo.output.replace(mo.md(""))
    else:
        _ump_stats = filtered.groupby("umpire").agg(
            challenges=("result", "size"),
            overturned=("result", lambda x: (x == "overturned").sum()),
        ).reset_index()
        _ump_stats["overturn_rate"] = (_ump_stats["overturned"] / _ump_stats["challenges"] * 100).round(1)
        _ump_stats = _ump_stats.sort_values("challenges", ascending=True).tail(15)

        _fig = go.Figure()
        _fig.add_trace(go.Bar(
            y=_ump_stats["umpire"],
            x=_ump_stats["overturned"],
            name="Overturned",
            orientation="h",
            marker_color="#ff6b6b",
            text=_ump_stats["overturn_rate"].apply(lambda x: f"{x:.0f}%"),
            textposition="auto",
        ))
        _fig.add_trace(go.Bar(
            y=_ump_stats["umpire"],
            x=_ump_stats["challenges"] - _ump_stats["overturned"],
            name="Upheld",
            orientation="h",
            marker_color="#51cf66",
        ))

        _fig.update_layout(
            barmode="stack",
            title="Umpire Challenge Counts",
            plot_bgcolor="#1a1b2e",
            paper_bgcolor="#1a1b2e",
            font=dict(color="white"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            height=500,
            xaxis=dict(title="Challenges", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )
        mo.output.replace(_fig)
    return


if __name__ == "__main__":
    app.run()
