import collections
from flaskr.utils import ByeWeek, LoadMatchups, NumberOfWeeks, LatestSeason, LoadData
from flaskr.globals import LEAGUE_ID, FIRST_SEASON

def results(start_year, end_year, playoffs, count, blowouts):
    all_matchups = {}
    start_year = start_year or FIRST_SEASON
    end_year = end_year or LatestSeason(LEAGUE_ID)

    for year in range(int(start_year), int(end_year) + 1):
        season = LoadData(year, LEAGUE_ID, 'mNav')
        matchups = LoadMatchups(year, LEAGUE_ID)
        weeks = NumberOfWeeks(year, LEAGUE_ID, playoffs)

        for idx, matchup in enumerate(matchups):
            matchup_id = f'{year}_{idx}'
            matchup_result = {}
            if matchup["matchupPeriodId"] > weeks:
                break

            if ByeWeek(matchup):
                continue

            away_dict = matchup["away"]["pointsByScoringPeriod"]
            away_score = next(iter(away_dict.values()))
            away_team_id = matchup["away"]["teamId"]

            if season["seasonId"] == year:
                for team in season["teams"]:
                    if team["id"] == away_team_id:
                        away_team_name = str(team["location"] + " " + team["nickname"])
                        break

            home_dict = matchup["home"]["pointsByScoringPeriod"]
            home_score = next(iter(home_dict.values()))
            home_team_id = matchup["home"]["teamId"]

            if season["seasonId"] == year:
                for team in season["teams"]:
                    if team["id"] == home_team_id:
                        home_team_name = str(team["location"] + " " + team["nickname"])
                        break

            difference = 0
            if away_score > home_score:
                difference = away_score - home_score
                winner = away_team_name
                loser = home_team_name
            else:
                difference = home_score - away_score
                winner = home_team_name
                loser = away_team_name

            matchup_result["year"] = year
            matchup_result["difference"] = round(difference, 2)
            matchup_result["winner"] = winner
            matchup_result["loser"] = loser

            all_matchups[matchup_id] = matchup_result

    sorted_blowouts = collections.OrderedDict(sorted(all_matchups.items(), key=lambda t:t[1]["difference"], reverse=blowouts))

    resp = {}
    for idx, x in enumerate(list(sorted_blowouts)[0:int(count)]):
        resp[idx+1] = sorted_blowouts[x]
    return resp