from flaskr.utils import ByeWeek, LoadMatchups, NumberOfWeeks
from flaskr.globals import LEAGUE_ID

def by_year(start_year, end_year, playoffs):
    all_records={}
    for year in range(start_year, end_year):
        matchups = LoadMatchups(year, LEAGUE_ID)
        weeks = NumberOfWeeks(year, LEAGUE_ID, playoffs)

        all_scores = []
        blowout_count = 0
        for matchup in matchups:
            if matchup["matchupPeriodId"] > weeks:
                break

            if ByeWeek(matchup):
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