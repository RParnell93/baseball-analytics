"""Database utilities for querying the baseball DuckDB."""

import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = str(Path(__file__).parent.parent.parent / "data" / "database" / "baseball.duckdb")


def query(sql: str, params: list = None) -> pd.DataFrame:
    """Run a SQL query against the baseball database and return a DataFrame."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        if params:
            result = con.execute(sql, params).fetchdf()
        else:
            result = con.execute(sql).fetchdf()
    finally:
        con.close()
    return result


def get_player_mlbam_id(name_first: str, name_last: str) -> int:
    """Look up a player's MLBAM ID from the player_ids table."""
    df = query("""
        SELECT key_mlbam FROM player_ids
        WHERE name_first = $1 AND name_last = $2
        AND key_mlbam IS NOT NULL
        ORDER BY mlb_played_last DESC NULLS LAST
        LIMIT 1
    """, [name_first, name_last])
    if len(df) == 0:
        raise ValueError(f"Player not found: {name_first} {name_last}")
    return int(df.iloc[0]["key_mlbam"])


def get_player_fg_id(name_first: str, name_last: str) -> int:
    """Look up a player's FanGraphs ID from the player_ids table."""
    df = query("""
        SELECT key_fangraphs FROM player_ids
        WHERE name_first = $1 AND name_last = $2
        AND key_fangraphs IS NOT NULL
        ORDER BY mlb_played_last DESC NULLS LAST
        LIMIT 1
    """, [name_first, name_last])
    if len(df) == 0:
        raise ValueError(f"Player not found: {name_first} {name_last}")
    return int(df.iloc[0]["key_fangraphs"])


def batter_statcast(name_first: str, name_last: str, year: int = 2024) -> pd.DataFrame:
    """Get all Statcast pitches faced by a batter in a season."""
    mlbam_id = get_player_mlbam_id(name_first, name_last)
    return query(f"""
        SELECT * FROM statcast_pitches
        WHERE batter = {int(mlbam_id)}
        AND game_date >= '{int(year)}-01-01'
        AND game_date <= '{int(year)}-12-31'
        ORDER BY game_date, at_bat_number, pitch_number
    """)


def pitcher_statcast(name_first: str, name_last: str, year: int = 2024) -> pd.DataFrame:
    """Get all Statcast pitches thrown by a pitcher in a season."""
    mlbam_id = get_player_mlbam_id(name_first, name_last)
    return query(f"""
        SELECT * FROM statcast_pitches
        WHERE pitcher = {int(mlbam_id)}
        AND game_date >= '{int(year)}-01-01'
        AND game_date <= '{int(year)}-12-31'
        ORDER BY game_date, at_bat_number, pitch_number
    """)


def fg_batting_season(name: str = None, season: int = None, min_pa: int = 0) -> pd.DataFrame:
    """Get FanGraphs batting stats, optionally filtered."""
    where = ["1=1"]
    params = []
    if name:
        where.append(f"Name LIKE $${len(params) + 1}")
        params.append(f"%{name}%")
    if season:
        where.append(f"Season = {int(season)}")
    if min_pa > 0:
        where.append(f"PA >= {int(min_pa)}")
    return query(
        f"SELECT * FROM fg_batting WHERE {' AND '.join(where)} ORDER BY PA DESC",
        params if params else None,
    )


def fg_pitching_season(name: str = None, season: int = None, min_ip: float = 0) -> pd.DataFrame:
    """Get FanGraphs pitching stats, optionally filtered."""
    where = ["1=1"]
    params = []
    if name:
        where.append(f"Name LIKE $${len(params) + 1}")
        params.append(f"%{name}%")
    if season:
        where.append(f"Season = {int(season)}")
    if min_ip > 0:
        where.append(f"IP >= {float(min_ip)}")
    return query(
        f"SELECT * FROM fg_pitching WHERE {' AND '.join(where)} ORDER BY IP DESC",
        params if params else None,
    )
