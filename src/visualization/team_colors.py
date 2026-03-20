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


def _luminance(hex_color: str) -> float:
    """Relative luminance of a hex color (0=black, 1=white)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    # sRGB to linear
    r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_visible_color(team_abbr: str, bg_hex: str = "#232D3F") -> str:
    """Get a team color that's visible against the given background.

    Uses primary color if bright enough, otherwise falls back to secondary.
    If both are too dark, lightens the primary.
    """
    team = TEAM_COLORS.get(team_abbr.upper(), {})
    primary = team.get("primary", "#CCCCCC")
    secondary = team.get("secondary", "#CCCCCC")

    bg_lum = _luminance(bg_hex)
    pri_lum = _luminance(primary)
    sec_lum = _luminance(secondary)

    # WCAG contrast ratio threshold - need at least ~3:1 for readability
    min_contrast = 3.0
    pri_contrast = (pri_lum + 0.05) / (bg_lum + 0.05)
    sec_contrast = (sec_lum + 0.05) / (bg_lum + 0.05)

    if pri_contrast >= min_contrast:
        return primary
    if sec_contrast >= min_contrast:
        return secondary

    # Both too dark - lighten primary by blending toward white
    h = primary.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    factor = 0.5
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_team_name(team_abbr: str) -> str:
    """Get full team name from abbreviation."""
    return TEAM_COLORS.get(team_abbr.upper(), {}).get("name", team_abbr)


def all_primary_colors() -> dict:
    """Return dict of {abbreviation: primary_hex} for all teams."""
    return {k: v["primary"] for k, v in TEAM_COLORS.items()}
