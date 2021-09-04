import collections
from flaskr.utils import (
    active_teams,
    headshot,
    latest_season,
    load_data,
    player_info,
    team_logo
)
from flaskr.globals import LEAGUE_ID, FIRST_SEASON


def top_drafted():
    all_picks = {}
    start_year = FIRST_SEASON
    end_year = latest_season(LEAGUE_ID)

    mTeam = load_data(int(end_year), LEAGUE_ID, 'mTeam')
    active_team_ids = active_teams(mTeam)
    teams = mTeam["teams"]

    for year in range(int(start_year), int(end_year) + 1):
        players = player_info(year, LEAGUE_ID)
        draft_detail = load_data(year, LEAGUE_ID, 'mDraftDetail')
        picks = draft_detail["draftDetail"]["picks"]

        for pick in picks:
            team_id = pick["teamId"]
            if team_id not in active_team_ids:
                continue

            player = None
            player_id = pick["playerId"]

            for p in players:
                if p["id"] == player_id:
                    player = p
                    break
            if not player:
                continue

            player_name = player["player"]["fullName"]
            if player_id > 0:
                player_image = headshot(player_id)
            else:
                player_image = team_logo(player_name)

            team = next(t for t in teams if t["id"] == pick["teamId"])
            team_nickname = team["location"] + " " + team["nickname"]

            new_player_dict = {
                "player_name": player_name,
                "image": player_image,
                "picked": 1,
                "years": [year]
            }

            if team_id in all_picks:
                all_picks[team_id]["team_name"] = team_nickname
                all_picks[team_id]["logo"] = team.get("logo")
                if player_id in all_picks[team_id]["players"]:
                    player_dict = all_picks[team_id]["players"][player_id]
                    player_dict["picked"] += 1
                    player_dict["years"].append(year)
                else:
                    all_picks[team_id]["players"][player_id] = new_player_dict
            else:
                all_picks[team_id] = {
                    "team_name": team_nickname,
                    "logo": team.get("logo"),
                    "players": {
                        player_id: new_player_dict
                    }
                }

    teams_favorites = []
    for team in all_picks.values():
        sorted_picks = collections.OrderedDict(
            sorted(
                team["players"].items(),
                key=lambda t: t[1]["picked"],
                reverse=True
            )
        )

        top_picks = {}
        for idx, x in enumerate(list(sorted_picks)[0:3]):
            top_picks[idx+1] = sorted_picks[x]
        teams_favorites.append({
            "team_name": team["team_name"],
            "logo": team["logo"],
            "favorite_picks": top_picks
        })

    return teams_favorites
