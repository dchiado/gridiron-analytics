import json
import collections

from datetime import date
from flaskr.globals import FIRST_SEASON, LEAGUE_ID
from itertools import groupby


async def load_data(year, uri, session, week=None, headers=None):
    """Call the ESPN API based on arguments passed and current year.

    The format of the endpoint is different from pre-2019 and 2019-present
    so the format of the url depends on the year.

    Arguments:
        year (int) -- year data is needed for
        uri (str) -- the endpoint to hit, mTeam, mRoster, etc.
        session (aiohttp) -- the aiohttp session created in calling script
        week (int or None) -- week of season if it needs to be specified
        headers (object or None) -- headers to include in request

    Returns:
        resp_json (object) -- the data returned by the API
    """
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
    """Add necessary headers and call kona_player_info endpoint"""
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
    """Call mMatchupScore endpoint and return schedule sub-object"""
    resp = await load_data(year, 'mMatchupScore', session)
    return resp["schedule"]


async def load_transactions(year, session, week=None):
    """Call mTransactions2 endpoint and return transactions sub-object"""
    resp = await load_data(year, 'mTransactions2', session, week)
    return resp["transactions"]


async def number_of_weeks(year, playoffs, session):
    """Determine weeks in season depending on whether playoffs are included"""
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
    """Determine if matchup object is a bye"""
    if ("away" in matchup) and ("home" in matchup):
        return False
    else:
        return True


def team_name(team_id, season_obj):
    """Get team name from season object given team id"""
    for team in season_obj["teams"]:
        if team["id"] == team_id:
            return str(team["location"] + " " + team["nickname"])


async def team_mapping(year, session):
    """Create team id - team name mapping for given year"""
    mteam = await load_data(year, 'mTeam', session)
    m = {}
    for team in mteam["teams"]:
        m[team["id"]] = str(team["location"] + " " + team["nickname"])
    return m


def fantasy_team_logo(team_id, season_obj):
    """Find team logo URL from seasons object based on team id"""
    for team in season_obj["teams"]:
        if team["id"] == team_id:
            return team["logo"]


def print_to_file(content, file):
    """Write data to a file"""
    f = open(file, 'w')
    f.write(repr(content))
    f.close()


async def latest_season(session):
    """Find the latest/current fantasy season"""
    current = date.today().year
    resp = await load_data(current, 'mStatus', session)
    if not resp["draftDetail"]["drafted"]:
        return current - 1
    else:
        return current


def headshot(player_id):
    """Create player headshot URL based on player id"""
    return ("https://a.espncdn.com/i/headshots/nfl/players/full/" +
            str(player_id) + ".png")


def team_logo(team):
    """Create NFL team logo URL based on team id"""
    if "D/ST" in team:
        team = team.split()[0]
    abrev = team_abbreviation(team)
    return "https://a.espncdn.com/i/teamlogos/nfl/500/" + abrev + ".png"


def team_abbreviation(team):
    """Map team names from D/ST positions to abbreviations"""
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
    """Create list of active team id in the league"""
    teams = []
    for team in mteam["teams"]:
        teams.append(team["id"])
    return teams


def win_pct(win, loss):
    """Calculate win percentage"""
    pct = round((win / (win + loss))*100, 2)
    return str(pct) + '%'


def check_start_year(year):
    """Check year is not earlier than first season"""
    if year is None or int(year) < FIRST_SEASON:
        return FIRST_SEASON
    else:
        return int(year)


async def check_end_year(year, session):
    """Check year is not later than current season"""
    latest = await latest_season(session)
    if year is None or int(year) > latest:
        return latest
    else:
        return int(year)


def compare_lists(l1, l2):
    """Compare two lists, order independent"""
    return collections.Counter(l1) == collections.Counter(l2)


def current_streak(list):
    """First current streak given list of winners"""
    grouped = [[k, sum(1 for i in g)] for k, g in groupby(list)]
    return grouped[-1]


def longest_streak(list):
    """First longest anytime streak given list of winners"""
    grouped = [[k, sum(1 for i in g)] for k, g in groupby(list)]
    return sorted(grouped, key=lambda x: x[1], reverse=True)[0]
