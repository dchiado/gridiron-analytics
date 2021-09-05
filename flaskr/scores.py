import collections
from flaskr.utils import (
    check_end_year,
    is_bye_week,
    load_matchups,
    number_of_weeks,
    load_data,
    team_name,
    check_start_year
)


def best_and_worst_weeks(start_year, end_year, playoffs, count, highest):
    all_scores = {}
    start_year = check_start_year(start_year)
    end_year = check_end_year(end_year)

    for year in range(start_year, end_year + 1):
        weeks = number_of_weeks(year, playoffs)
        if weeks == 0:
            continue

        matchups = load_matchups(year)
        season = load_data(year, 'mNav')

        for matchup in matchups:
            week = 0
            if matchup["matchupPeriodId"] > weeks:
                break

            if is_bye_week(matchup):
                continue

            away_team_id = matchup["away"]["teamId"]
            if season["seasonId"] == year:
                away_team_name = team_name(away_team_id, season)

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
                home_team_name = team_name(home_team_id, season)

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

    sorted_scores = collections.OrderedDict(
        sorted(
            all_scores.items(), key=lambda t: t[1]["score"], reverse=highest
            )
        )

    resp = {}
    for idx, x in enumerate(list(sorted_scores)[0:int(count)]):
        resp[idx+1] = sorted_scores[x]
    return resp


def highest_weeks(start_year, end_year, playoffs):
    return best_and_worst_weeks(start_year, end_year, playoffs, True)


def lowest_weeks(start_year, end_year, playoffs):
    return best_and_worst_weeks(start_year, end_year, playoffs, False)


def best_and_worst_seasons(start_year, end_year, count, best):
    all_seasons_all_time = {}

    start_year = check_start_year(start_year)
    end_year = check_end_year(end_year)

    for year in range(int(start_year), int(end_year) + 1):
        all_averages_this_year = []
        all_seasons_this_year = []

        season = load_data(year, 'mNav')
        current_year_teams = season["teams"]

        matchups = load_matchups(year)
        weeks = number_of_weeks(year, False)
        if weeks == 0:
            continue

        for team in current_year_teams:
            current_team_id = team["id"]
            current_team_name = team_name(current_team_id, season)

            total_points = 0

            for matchup in matchups:
                if matchup["matchupPeriodId"] > weeks:
                    break

                if is_bye_week(matchup):
                    continue

                if matchup["away"]["teamId"] == current_team_id:
                    total_points += matchup["away"]["totalPoints"]

                if matchup["home"]["teamId"] == current_team_id:
                    total_points += matchup["home"]["totalPoints"]

            average_team_score = total_points / weeks
            all_seasons_this_year.append({
                    "year": year,
                    "team_name": current_team_name,
                    "average": round(average_team_score, 2)
                }
            )
            all_averages_this_year.append(round(average_team_score, 2))

        league_average = round(
            sum(all_averages_this_year) / len(all_averages_this_year), 2
        )

        for season in all_seasons_this_year:
            team_average = season["average"]
            pct_diff_from_league = (
                (team_average - league_average) / league_average * 100
            )
            season["league_average"] = league_average
            season["pct_diff"] = round(pct_diff_from_league, 2)

            id = f'{year} {season["team_name"]}'
            all_seasons_all_time[id] = season

    sorted_top_seasons = collections.OrderedDict(
        sorted(
            all_seasons_all_time.items(),
            key=lambda t: t[1]["pct_diff"],
            reverse=best
        )
    )

    resp = {}
    for idx, x in enumerate(list(sorted_top_seasons)[0:int(count)]):
        resp[idx+1] = sorted_top_seasons[x]
    return resp
