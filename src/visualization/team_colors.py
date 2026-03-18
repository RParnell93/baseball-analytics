"""MLB team color definitions for consistent visualization branding."""

# Primary and secondary colors for all 30 MLB teams
# Source: official team brand guidelines
TEAM_COLORS = {
    "ARI": {"primary": "#A71930", "secondary": "#E3D4AD", "name": "Arizona Diamondbacks"},
    "ATL": {"primary": "#CE1141", "secondary": "#13274F", "name": "Atlanta Braves"},
    "BAL": {"primary": "#DF4601", "secondary": "#000000", "name": "Baltimore Orioles"},
    "BOS": {"primary": "#BD3039", "secondary": "#0C2340", "name": "Boston Red Sox"},
    "CHC": {"primary": "#0E3386", "secondary": "#CC3433", "name": "Chicago Cubs"},
    "CHW": {"primary": "#27251F", "secondary": "#C4CED4", "name": "Chicago White Sox"},
    "CIN": {"primary": "#C6011F", "secondary": "#000000", "name": "Cincinnati Reds"},
    "CLE": {"primary": "#00385D", "secondary": "#E50022", "name": "Cleveland Guardians"},
    "COL": {"primary": "#33006F", "secondary": "#C4CED4", "name": "Colorado Rockies"},
    "DET": {"primary": "#0C2340", "secondary": "#FA4616", "name": "Detroit Tigers"},
    "HOU": {"primary": "#002D62", "secondary": "#EB6E1F", "name": "Houston Astros"},
    "KC":  {"primary": "#004687", "secondary": "#BD9B60", "name": "Kansas City Royals"},
    "LAA": {"primary": "#BA0021", "secondary": "#003263", "name": "Los Angeles Angels"},
    "LAD": {"primary": "#005A9C", "secondary": "#A5ACAF", "name": "Los Angeles Dodgers"},
    "MIA": {"primary": "#00A3E0", "secondary": "#EF3340", "name": "Miami Marlins"},
    "MIL": {"primary": "#FFC52F", "secondary": "#12284B", "name": "Milwaukee Brewers"},
    "MIN": {"primary": "#002B5C", "secondary": "#D31145", "name": "Minnesota Twins"},
    "NYM": {"primary": "#002D72", "secondary": "#FF5910", "name": "New York Mets"},
    "NYY": {"primary": "#003087", "secondary": "#C4CED4", "name": "New York Yankees"},
    "OAK": {"primary": "#003831", "secondary": "#EFB21E", "name": "Oakland Athletics"},
    "PHI": {"primary": "#E81828", "secondary": "#002D72", "name": "Philadelphia Phillies"},
    "PIT": {"primary": "#27251F", "secondary": "#FDB827", "name": "Pittsburgh Pirates"},
    "SD":  {"primary": "#2F241D", "secondary": "#FFC425", "name": "San Diego Padres"},
    "SF":  {"primary": "#FD5A1E", "secondary": "#27251F", "name": "San Francisco Giants"},
    "SEA": {"primary": "#0C2C56", "secondary": "#005C5C", "name": "Seattle Mariners"},
    "STL": {"primary": "#C41E3A", "secondary": "#0C2340", "name": "St. Louis Cardinals"},
    "TB":  {"primary": "#092C5C", "secondary": "#8FBCE6", "name": "Tampa Bay Rays"},
    "TEX": {"primary": "#003278", "secondary": "#C0111F", "name": "Texas Rangers"},
    "TOR": {"primary": "#134A8E", "secondary": "#1D2D5C", "name": "Toronto Blue Jays"},
    "WSH": {"primary": "#AB0003", "secondary": "#14225A", "name": "Washington Nationals"},
}


def get_color(team_abbr: str, which: str = "primary") -> str:
    """Get a team's color by abbreviation. Returns hex string."""
    team = TEAM_COLORS.get(team_abbr.upper(), {})
    return team.get(which, "#333333")


def get_team_name(team_abbr: str) -> str:
    """Get full team name from abbreviation."""
    return TEAM_COLORS.get(team_abbr.upper(), {}).get("name", team_abbr)


def all_primary_colors() -> dict:
    """Return dict of {abbreviation: primary_hex} for all teams."""
    return {k: v["primary"] for k, v in TEAM_COLORS.items()}
