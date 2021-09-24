from flaskr.utils import (
    is_bye_week,
    load_matchups,
    number_of_weeks,
    check_start_year,
    check_end_year
)
import aiohttp


async def by_year(start_year, end_year, playoffs):
    """Calculate number of blowouts (>50 pt wins) by year.

    Arguments:
        start_year (str or None) -- the first year to check
        end_year (str or None) -- the last year to check
        playoffs (bool) -- whether or not to include playoffs

    Returns:
        all_records (object) -- blowouts and avg score by year
        {
            2008: {
                "blowout_count": 10,
                "average_score": 85.62
            },
            2009: {...}
        }
    """
    async with aiohttp.ClientSession() as session:
        all_records = {}
        start_year = check_start_year(start_year)
        end_year = await check_end_year(end_year, session)

        for year in range(int(start_year), int(end_year) + 1):
            weeks = await number_of_weeks(year, playoffs, session)
            if weeks == 0:
                continue

            matchups = await load_matchups(year, session)

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

        print(all_records)
        return all_records
