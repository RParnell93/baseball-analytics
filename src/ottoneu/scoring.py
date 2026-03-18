"""Ottoneu FGPts and SABR scoring calculators.

Given a row of player stats (from FanGraphs or raw data), calculate
total points per game format. Use these to project player value.
"""

import pandas as pd


# FGPts (FanGraphs Points) scoring weights
FGPTS_BATTING = {
    "AB": -1.0,
    "H": 5.6,
    "2B": 2.9,
    "3B": 5.7,
    "HR": 9.4,
    "BB": 3.0,
    "HBP": 3.0,
    "SB": 1.9,
    "CS": -2.8,
}

FGPTS_PITCHING = {
    "IP": 7.4,
    "SO": 2.0,
    "H": -2.6,
    "BB": -3.0,
    "HBP": -3.0,
    "HR": -12.3,
    "SV": 5.0,
    "HLD": 4.0,
}

# SABR Points scoring weights (same hitting, FIP-based pitching)
SABR_BATTING = FGPTS_BATTING.copy()

SABR_PITCHING = {
    "IP": 5.0,
    "SO": 2.0,
    "BB": -3.0,
    "HBP": -3.0,
    "HR": -13.0,
    "SV": 5.0,
    "HLD": 4.0,
}


def calc_batting_points(row, format="fgpts"):
    """Calculate batting points for a single player-season row.

    Args:
        row: dict-like with stat keys (AB, H, 2B, 3B, HR, BB, HBP, SB, CS)
        format: "fgpts" or "sabr"

    Returns:
        float: total points
    """
    weights = FGPTS_BATTING if format == "fgpts" else SABR_BATTING
    total = 0.0
    for stat, weight in weights.items():
        val = row.get(stat, 0)
        if pd.isna(val):
            val = 0
        total += val * weight
    return total


def calc_pitching_points(row, format="fgpts"):
    """Calculate pitching points for a single player-season row.

    Args:
        row: dict-like with stat keys (IP, SO, H, BB, HBP, HR, SV, HLD)
        format: "fgpts" or "sabr"

    Returns:
        float: total points
    """
    weights = FGPTS_PITCHING if format == "fgpts" else SABR_PITCHING
    total = 0.0
    for stat, weight in weights.items():
        val = row.get(stat, 0)
        if pd.isna(val):
            val = 0
        total += val * weight
    return total


def score_batting_df(df, format="fgpts"):
    """Add a points column to a batting DataFrame.

    Expects FanGraphs column names. Maps common aliases.
    """
    # Map FanGraphs column names to scoring names
    col_map = {"SO": "SO", "K": "SO"}  # FG uses SO
    mapped = df.rename(columns=col_map)

    points = mapped.apply(lambda r: calc_batting_points(r, format), axis=1)
    result = df.copy()
    result[f"{format}_points"] = points
    return result


def score_pitching_df(df, format="fgpts"):
    """Add a points column to a pitching DataFrame.

    Expects FanGraphs column names.
    """
    points = df.apply(lambda r: calc_pitching_points(r, format), axis=1)
    result = df.copy()
    result[f"{format}_points"] = points
    return result


def points_per_game(points, games):
    """Calculate points per game (P/G), the key Ottoneu rate stat."""
    if games == 0:
        return 0.0
    return points / games


def points_per_ip(points, ip):
    """Calculate points per inning pitched (P/IP) for pitchers."""
    if ip == 0:
        return 0.0
    return points / ip
