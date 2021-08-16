import requests
from datetime import date
from flaskr.globals import LEAGUE_ID

def LoadData(year, league_id, uri):
    if year > 2019:
        url = "http://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
            str(year) + "/segments/0/leagues/" + str(league_id) + "?&view=" + uri
        return requests.get(url).json()
    else:
        url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
            str(league_id) + "?seasonId=" + str(year) + "&view=" + uri
        return requests.get(url).json()[0]

def LoadMatchups(year, league_id):
    matchups = LoadData(year, league_id, 'mMatchupScore')
    return matchups["schedule"]

def NumberOfWeeks(year, league_id, playoffs):
    season = LoadData(year, league_id, 'mSettings')

    current_week = season["status"]["latestScoringPeriod"]
    total_weeks = season["status"]["finalScoringPeriod"]
    regular_season_weeks = season["settings"]["scheduleSettings"]["matchupPeriodCount"]

    if playoffs and (current_week <= total_weeks):
        return current_week - 1 
    elif playoffs and (current_week > total_weeks):
        return total_weeks
    elif current_week <= regular_season_weeks:
        return current_week - 1
    else:
        return regular_season_weeks

def ByeWeek(matchup):
    if ("away" in matchup) and ("home" in matchup):
        return False
    else:
        return True

def StartYear(only_current_scoring_rules, only_current_teams):
    if only_current_scoring_rules:
        return 2016
    elif only_current_teams:
        return 2014
    else:
        return 2005

def TeamName(team_id, year, season_obj):
      for team in season_obj["teams"]:
          if team["id"] == team_id:
              return str(team["location"] + " " + team["nickname"])

def PrintToFile(content, file):
    f = open( file, 'w' )
    f.write(repr(content))
    f.close()

def LatestSeason(league_id):
    current = date.today().year
    res = LoadData(current, league_id, 'mStatus')
    if res["draftDetail"]["drafted"] == False:
        return current - 1
    else:
        return current
