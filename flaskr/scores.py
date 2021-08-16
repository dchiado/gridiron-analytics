import collections
from flaskr.utils import ByeWeek, LoadMatchups, NumberOfWeeks, LatestSeason, LoadData, TeamName
from flaskr.globals import LEAGUE_ID, FIRST_SEASON

def best_and_worst(start_year, end_year, playoffs, highest):
    start_year = start_year or FIRST_SEASON
    end_year = end_year or LatestSeason(LEAGUE_ID)
    all_scores = {}

    for year in range(start_year, end_year):
        matchups = LoadMatchups(year, LEAGUE_ID)
        weeks = NumberOfWeeks(year, LEAGUE_ID, playoffs)
        season = LoadData(year, LEAGUE_ID, 'mNav')

        for matchup in matchups:
            week = 0
            if matchup["matchupPeriodId"] > weeks:
                break

            if ByeWeek(matchup):
                continue

            away_team_id = matchup["away"]["teamId"]
            if season["seasonId"] == year:
                for team in season["teams"]:
                    if team["id"] == away_team_id:
                        away_team_name = str(team["location"] + " " + team["nickname"])
                        break

            away_dict = matchup["away"]["pointsByScoringPeriod"]
            away_score = next(iter(away_dict.values()))
            week = matchup["matchupPeriodId"]
            away_game = {
                "year": year,
                "week": week,
                "team_name": away_team_name,
                "score": away_score
            }
            all_scores[f'{year} {week} {away_team_name}'] = away_game

            home_team_id = matchup["home"]["teamId"]
            if season["seasonId"] == year:
                for team in season["teams"]:
                    if team["id"] == home_team_id:
                        home_team_name = str(team["location"] + " " + team["nickname"])
                        break

            home_dict = matchup["home"]["pointsByScoringPeriod"]
            home_score = next(iter(home_dict.values()))
            week = matchup["matchupPeriodId"]
            home_game = {
                "year": year,
                "week": week,
                "team_name": home_team_name,
                "score": home_score
            }
            all_scores[f'{year} {week} {home_team_name}'] = home_game

    print("Highest Scores (with current scoring settings)")
    print("Year,Week,Team,Score")
    sorted_scores = collections.OrderedDict(sorted(all_scores.items(), key=lambda t:t[1]["score"], reverse=highest))
    return list(sorted_scores.items())[:10]

def highest_weeks(start_year, end_year, playoffs):
    return best_and_worst(start_year, end_year, playoffs, True)

def lowest_weeks(start_year, end_year, playoffs):
    return best_and_worst(start_year, end_year, playoffs, False)

def yearly_league_wide(start_year, end_year, playoffs, best):
    all_seasons_all_time = {}

    start_year = start_year or FIRST_SEASON
    end_year = end_year or LatestSeason(LEAGUE_ID)

    for year in range(int(start_year), int(end_year) + 1):
        all_averages_this_year = []
        all_seasons_this_year = []

        season = LoadData(year, LEAGUE_ID, 'mNav')

        if season["seasonId"] == year:
            current_year_teams = season["teams"]

        matchups = LoadMatchups(year, LEAGUE_ID)
        weeks = NumberOfWeeks(year, LEAGUE_ID, playoffs)

        for team in current_year_teams:
            team_id = team["id"]
            team_name = TeamName(team_id, year)

            total_points = 0

            for matchup in matchups:
                if matchup["matchupPeriodId"] > weeks:
                    break

                if ByeWeek(matchup):
                    continue

                game = []
                if matchup["away"]["teamId"] == team_id:
                    total_points += matchup["away"]["totalPoints"]
                
                if matchup["home"]["teamId"] == team_id:
                    total_points += matchup["home"]["totalPoints"]

            average_team_score = total_points / weeks
            all_seasons_this_year.append({
                    "year": year,
                    "team_name": team_name,
                    "average": round(average_team_score, 2)
                }
            )
            all_averages_this_year.append(round(average_team_score, 2))
        
        league_average = round(sum(all_averages_this_year) / len(all_averages_this_year), 2)
        for season in all_seasons_this_year:
            team_average = season["average"]
            pct_diff_from_league = (team_average - league_average) / league_average * 100
            season["league_average"] = league_average
            season["pct_diff"] = round(pct_diff_from_league, 2)

            id = f'{year} {season["team_name"]}'
            all_seasons_all_time[id] = season

        all_seasons_this_year.append({
                "year": year,
                "team_name": 'AVERAGE',
                "average": league_average,
                "league_average": league_average,
                "pct_diff": 0.00
            }
        )

    sorted_top_seasons = collections.OrderedDict(sorted(all_seasons_all_time.items(), key=lambda t:t[1]["pct_diff"], reverse=best))
    return sorted_top_seasons
