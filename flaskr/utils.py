import requests
import json
from datetime import date


def load_data(year, league_id, uri, headers=None):
    if year > 2019:
        url = "http://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
            str(year) + "/segments/0/leagues/" + str(league_id) + \
            "?&view=" + uri
        return requests.get(url, headers=headers).json()
    else:
        url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
            str(league_id) + "?seasonId=" + str(year) + "&view=" + uri
        return requests.get(url, headers=headers).json()[0]


def player_info(year, league_id):
    filters = {
        "players": {
            "limit": 1500,
            "sortDraftRanks": {
                "sortPriority": 100,
                "sortAsc": True,
                "value": "STANDARD"
            }
        }
    }
    headers = {'x-fantasy-filter': json.dumps(filters)}
    return load_data(year, league_id, 'kona_player_info', headers)["players"]


def load_matchups(year, league_id):
    return load_data(year, league_id, 'mMatchupScore')["schedule"]


def number_of_weeks(year, league_id, playoffs):
    season = load_data(year, league_id, 'mSettings')

    current_week = season["status"]["latestScoringPeriod"]
    total_weeks = season["status"]["finalScoringPeriod"]
    regular_season_weeks = (
        season["settings"]["scheduleSettings"]["matchupPeriodCount"]
    )

    if playoffs and (current_week <= total_weeks):
        return current_week - 1
    elif playoffs and (current_week > total_weeks):
        return total_weeks
    elif current_week <= regular_season_weeks:
        return current_week - 1
    else:
        return regular_season_weeks


def is_bye_week(matchup):
    if ("away" in matchup) and ("home" in matchup):
        return False
    else:
        return True


def start_year(only_current_scoring_rules, only_current_teams):
    if only_current_scoring_rules:
        return 2016
    elif only_current_teams:
        return 2014
    else:
        return 2005


def team_name(team_id, season_obj):
    for team in season_obj["teams"]:
        if team["id"] == team_id:
            return str(team["location"] + " " + team["nickname"])


def print_to_file(content, file):
    f = open(file, 'w')
    f.write(repr(content))
    f.close()


def latest_season(league_id):
    current = date.today().year
    res = load_data(current, league_id, 'mStatus')
    if not res["draftDetail"]["drafted"]:
        return current - 1
    else:
        return current
