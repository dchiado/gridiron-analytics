import json
import collections

from datetime import date
from flaskr.globals import FIRST_SEASON, LEAGUE_ID
from itertools import groupby


async def load_data(year, uri, session, week=None, headers=None):
    if year > 2019:
        url = (
          "http://fantasy.espn.com/apis/v3/games/ffl/seasons/" + str(year) +
          "/segments/0/leagues/" + str(LEAGUE_ID) +
          "?&view=" + uri +
          ("&scoringPeriodId=" + str(week) if week is not None else '')
        )
        resp = await session.request(method='GET', url=url, headers=headers)
        resp_json = await resp.json()
        return resp_json
    else:
        url = (
          "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" +
          str(LEAGUE_ID) +
          "?seasonId=" + str(year) +
          "&view=" + uri +
          ("&scoringPeriodId=" + str(week) if week is not None else '')
        )
        resp = await session.request(method='GET', url=url, headers=headers)
        resp_json = await resp.json()
        return resp_json[0]


async def player_info(year, session):
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
    resp = await load_data(year, 'kona_player_info', session, headers=headers)
    return resp["players"]


async def load_matchups(year, session):
    resp = await load_data(year, 'mMatchupScore', session)
    return resp["schedule"]


async def load_transactions(year, session, week=None):
    resp = await load_data(year, 'mTransactions2', session, week)
    return resp["transactions"]


async def number_of_weeks(year, playoffs, session):
    season = await load_data(year, 'mSettings', session)

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


def team_name(team_id, season_obj):
    for team in season_obj["teams"]:
        if team["id"] == team_id:
            return str(team["location"] + " " + team["nickname"])


async def team_mapping(year, session):
    mTeam = await load_data(year, 'mTeam', session)
    m = {}
    for team in mTeam["teams"]:
        m[team["id"]] = str(team["location"] + " " + team["nickname"])
    return m


def fantasy_team_logo(team_id, season_obj):
    for team in season_obj["teams"]:
        if team["id"] == team_id:
            return team["logo"]


def print_to_file(content, file):
    f = open(file, 'w')
    f.write(repr(content))
    f.close()


async def latest_season(session):
    current = date.today().year
    resp = await load_data(current, 'mStatus', session)
    if not resp["draftDetail"]["drafted"]:
        return current - 1
    else:
        return current


def headshot(player_id):
    return ("https://a.espncdn.com/i/headshots/nfl/players/full/" +
            str(player_id) + ".png")


def team_logo(team):
    if "D/ST" in team:
        team = team.split()[0]
    abrev = team_abbreviation(team)
    return "https://a.espncdn.com/i/teamlogos/nfl/500/" + abrev + ".png"


def team_abbreviation(team):
    abbreviations = {
        "49ers": "sf",
        "Bears": "chi",
        "Bengals": "cin",
        "Bills": "buf",
        "Broncos": "den",
        "Browns": "cle",
        "Buccaneers": "tb",
        "Cardinals": "ari",
        "Chargers": "lac",
        "Chiefs": "kc",
        "Colts": "ind",
        "Cowboys": "dal",
        "Dolphins": "mia",
        "Eagles": "phi",
        "Falcons": "atl",
        "Football Team": "was",
        "Giants": "nyg",
        "Jaguars": "jax",
        "Jets": "nyj",
        "Lions": "det",
        "Packers": "gb",
        "Panthers": "car",
        "Patriots": "ne",
        "Raiders": "lv",
        "Rams": "lar",
        "Ravens": "bal",
        "Redskins": "was",
        "Saints": "no",
        "Seahawks": "sea",
        "Steelers": "pit",
        "Texans": "hou",
        "Titans": "ten",
        "Vikings": "min",
        "Washington": "was"
    }
    return abbreviations[team]


def active_teams(mteam):
    teams = []
    for team in mteam["teams"]:
        teams.append(team["id"])
    return teams


def win_pct(win, loss):
    pct = round((win / (win + loss))*100, 2)
    return str(pct) + '%'


def check_start_year(year):
    if year is None or int(year) < FIRST_SEASON:
        return FIRST_SEASON
    else:
        return int(year)


async def check_end_year(year, session):
    latest = await latest_season(session)
    if year is None or int(year) > latest:
        return latest
    else:
        return int(year)


def compare_lists(l1, l2):
    return collections.Counter(l1) == collections.Counter(l2)


def current_streak(list):
    grouped = [[k, sum(1 for i in g)] for k, g in groupby(list)]
    return grouped[-1]


def longest_streak(list):
    grouped = [[k, sum(1 for i in g)] for k, g in groupby(list)]
    return sorted(grouped, key=lambda x: x[1], reverse=True)[0]
