"""Ottoneu client - login, roster management, lineup setting.

Authenticates via FanGraphs WordPress login, then interacts with
Ottoneu endpoints for roster data and lineup changes.
"""

import os
import re
import csv
import io
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

OTTONEU_BASE = "https://ottoneu.fangraphs.com"
FG_LOGIN_URL = "https://blogs.fangraphs.com/wp-login.php"


class OttoneuClient:
    """Authenticated Ottoneu client."""

    def __init__(self, username=None, password=None):
        self.username = username or os.getenv("OTTONEU_USERNAME")
        self.password = password or os.getenv("OTTONEU_PASSWORD")
        self.session = requests.Session()
        self._logged_in = False

    def login(self):
        """Authenticate via FanGraphs WordPress login."""
        if not self.username or not self.password:
            raise ValueError("OTTONEU_USERNAME and OTTONEU_PASSWORD must be set in .env")

        self.session.get(FG_LOGIN_URL, params={"redirect_to": OTTONEU_BASE})
        r = self.session.post(FG_LOGIN_URL, data={
            "log": self.username,
            "pwd": self.password,
            "wp-submit": "Log In",
            "redirect_to": OTTONEU_BASE,
            "testcookie": "1",
        }, allow_redirects=True)

        if "userdashboard" in r.url:
            self._logged_in = True
            return True

        raise ConnectionError("Login failed - check credentials")

    def _ensure_login(self):
        if not self._logged_in:
            self.login()

    def get_leagues(self):
        """Get all leagues for the authenticated user.

        Returns list of dicts with league_id and name.
        """
        self._ensure_login()
        r = self.session.get(f"{OTTONEU_BASE}/userdashboard")
        leagues = re.findall(r'href="/(\d+)/home"[^>]*>([^<]+)', r.text)
        return [{"league_id": int(lid), "name": name.strip()} for lid, name in leagues]

    def get_roster(self, league_id):
        """Get full roster for a league via CSV export.

        Returns list of dicts with player info.
        """
        self._ensure_login()
        r = self.session.get(f"{OTTONEU_BASE}/{league_id}/rosterexport")
        if r.status_code != 200:
            raise ConnectionError(f"Roster export failed: {r.status_code}")

        reader = csv.DictReader(io.StringIO(r.text))
        return list(reader)

    def get_my_roster(self, league_id, team_id):
        """Get just your team's roster from a league.

        Returns list of player dicts.
        """
        roster = self.get_roster(league_id)
        return [p for p in roster if p.get("TeamID") == str(team_id)]

    def get_lineup(self, league_id, target_date=None):
        """Get current lineup positions from the setlineups page.

        Returns list of dicts with ottoneu_id, name, position (current slot),
        eligible_positions, salary, is_pitcher, team.
        """
        self._ensure_login()
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")
        r = self.session.get(f"{OTTONEU_BASE}/{league_id}/setlineups?date={date_str}")

        # Extract the actual date the server is showing (may differ from requested)
        init_match = re.search(r'lineups\.init\([^,]+,\s*\d+,\s*"(\d{4}-\d{2}-\d{2})"', r.text)
        self._last_lineup_date = init_match.group(1) if init_match else date_str

        players = []
        pattern = re.compile(
            r'<td\s+data-player-id="(\d+)"\s+'
            r'data-position="([^"]+)"\s+'
            r'data-player-positions="([^"]*)"\s+'
            r'data-is-pitcher="([^"]+)"\s+'
            r'data-is-position-player="([^"]+)"\s+'
            r'data-is-pitcher-version-of-two-way-player="([^"]+)"\s+'
            r'class="lineup__button[^"]*">[^<]*</td>\s*'
            r'<td\s+class="player-name[^"]*">\s*'
            r'(?:<a[^>]*>([^<]*)</a>|<span[^>]*>([^<]*)</span>)',
            re.DOTALL
        )

        for m in pattern.finditer(r.text):
            otto_id = m.group(1)
            position = m.group(2)
            eligible = m.group(3)
            is_pitcher = m.group(4) == "true"
            is_position = m.group(5) == "true"
            is_two_way_p = m.group(6) == "true"
            name = (m.group(7) or m.group(8) or "").strip()

            # Get salary and MLB team from nearby HTML
            row_start = m.start()
            row_chunk = r.text[row_start:row_start + 800]
            salary_match = re.search(r'\$(\d+)', row_chunk)
            team_match = re.search(r'<span class="strong tinytext">(\w+)', row_chunk)

            players.append({
                "ottoneu_id": int(otto_id),
                "name": name,
                "position": position,
                "eligible_positions": eligible.split(",") if eligible else [],
                "is_pitcher": is_pitcher,
                "is_position_player": is_position,
                "is_two_way_pitcher": is_two_way_p,
                "salary": int(salary_match.group(1)) if salary_match else 0,
                "mlb_team": team_match.group(1) if team_match else "",
            })

        return players

    def set_lineup(self, league_id, changes, target_date=None):
        """Set lineup positions for players.

        Args:
            league_id: Ottoneu league ID
            changes: list of dicts, each with:
                - player_id: ottoneu player ID
                - old_position: current position slot (e.g. "Bench")
                - new_position: target position slot (e.g. "SP")
                - is_two_way_pitcher: bool (default False)
            target_date: date for the lineup (default today)

        Returns:
            dict with ErrorCode (0 = success) and ErrorMessage/SuccessfulChanges
        """
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")

        self._ensure_login()

        # Fresh session per lineup change to avoid "already moved" (ErrorCode=2).
        # Copy auth cookies from main session but get a new PHPSESSID.
        s = requests.Session()
        for cookie in self.session.cookies:
            if cookie.name != "PHPSESSID":
                s.cookies.set_cookie(cookie)

        # Visit setlineups to establish server state.
        # The server may redirect to the next game date - extract the actual date
        # from lineups.init() to use in the POST.
        page = s.get(
            f"{OTTONEU_BASE}/{league_id}/setlineups?date={date_str}",
            timeout=30,
        )
        init_match = re.search(r'lineups\.init\([^,]+,\s*\d+,\s*"(\d{4}-\d{2}-\d{2})"', page.text)
        actual_date = init_match.group(1) if init_match else date_str

        # jQuery-style nested form data (not JSON)
        form_data = {
            "method": "saveChanges",
            "data[Date]": actual_date,
            "data[VisibleSplit]": "season",
        }
        for i, c in enumerate(changes):
            form_data[f"data[Changes][{i}][PlayerID]"] = c["player_id"]
            form_data[f"data[Changes][{i}][OldPosition]"] = c["old_position"]
            form_data[f"data[Changes][{i}][NewPosition]"] = c["new_position"]
            form_data[f"data[Changes][{i}][IsPitcherVersionOfTwoWayPlayer]"] = (
                "true" if c.get("is_two_way_pitcher") else "false"
            )

        r = s.post(
            f"{OTTONEU_BASE}/{league_id}/ajax/setlineups",
            data=form_data,
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{OTTONEU_BASE}/{league_id}/setlineups?date={actual_date}",
            },
        )

        return r.json()

    def swap_players(self, league_id, player_a_id, player_b_id, target_date=None):
        """Swap two players' lineup positions.

        Convenience method - looks up current positions and swaps them.
        """
        lineup = self.get_lineup(league_id, target_date)

        player_a = next((p for p in lineup if p["ottoneu_id"] == player_a_id), None)
        player_b = next((p for p in lineup if p["ottoneu_id"] == player_b_id), None)

        if not player_a:
            raise ValueError(f"Player {player_a_id} not found in lineup")
        if not player_b:
            raise ValueError(f"Player {player_b_id} not found in lineup")

        changes = [
            {
                "player_id": player_a_id,
                "old_position": player_a["position"],
                "new_position": player_b["position"],
                "is_two_way_pitcher": player_a["is_two_way_pitcher"],
            },
            {
                "player_id": player_b_id,
                "old_position": player_b["position"],
                "new_position": player_a["position"],
                "is_two_way_pitcher": player_b["is_two_way_pitcher"],
            },
        ]

        return self.set_lineup(league_id, changes, target_date)

    def move_to_lineup(self, league_id, player_id, new_position, target_date=None):
        """Move a single player to a new lineup position.

        If someone is already in that slot, they go to Bench.
        """
        lineup = self.get_lineup(league_id, target_date)

        player = next((p for p in lineup if p["ottoneu_id"] == player_id), None)
        if not player:
            raise ValueError(f"Player {player_id} not found in lineup")

        # Find who's currently in the target position (skip Bench/Minors - multiple allowed)
        occupant = None
        if new_position not in ("Bench", "Minors"):
            occupant = next((p for p in lineup if p["position"] == new_position), None)

        changes = []
        if occupant and occupant["ottoneu_id"] != player_id:
            # Swap: occupant goes to player's old spot
            changes.append({
                "player_id": occupant["ottoneu_id"],
                "old_position": new_position,
                "new_position": player["position"],
                "is_two_way_pitcher": occupant["is_two_way_pitcher"],
            })

        changes.append({
            "player_id": player_id,
            "old_position": player["position"],
            "new_position": new_position,
            "is_two_way_pitcher": player["is_two_way_pitcher"],
        })

        return self.set_lineup(league_id, changes, target_date)

    def bench_player(self, league_id, player_id, target_date=None):
        """Move a player to the bench."""
        return self.move_to_lineup(league_id, player_id, "Bench", target_date)

    def activate_player(self, league_id, player_id, position, target_date=None):
        """Move a player from bench/minors to an active lineup slot."""
        return self.move_to_lineup(league_id, player_id, position, target_date)
