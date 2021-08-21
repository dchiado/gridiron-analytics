from flaskr.utils import (
    is_bye_week,
    load_matchups,
    number_of_weeks,
    latest_season
)
from flaskr.globals import LEAGUE_ID, FIRST_SEASON


def by_year(start_year, end_year, playoffs):
    all_records = {}
    start_year = start_year or FIRST_SEASON
    end_year = end_year or latest_season(LEAGUE_ID)

    for year in range(int(start_year), int(end_year) + 1):
        matchups = load_matchups(year, LEAGUE_ID)
        weeks = number_of_weeks(year, LEAGUE_ID, playoffs)

        all_scores = []
        blowout_count = 0
        for matchup in matchups:
            if matchup["matchupPeriodId"] > weeks:
                break

            if is_bye_week(matchup):
                break

            away_dict = matchup["away"]["pointsByScoringPeriod"]
            home_dict = matchup["home"]["pointsByScoringPeriod"]
            away_score = next(iter(away_dict.values()))
            home_score = next(iter(home_dict.values()))
            all_scores.append(away_score)
            all_scores.append(home_score)

            difference = 0
            if away_score > home_score:
                difference = away_score - home_score
            else:
                difference = home_score - away_score

            if difference > 50.0:
                blowout_count += 1

        average_score = sum(all_scores) / len(all_scores)

        all_records[year] = {
            "blowout_count": blowout_count,
            "average_score": average_score
        }

    return all_records
