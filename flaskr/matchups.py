import collections
import aiohttp
from flaskr.utils import (
    is_bye_week,
    load_matchups,
    number_of_weeks,
    check_start_year,
    check_end_year,
    load_data,
    team_name
)


async def results(start_year, end_year, playoffs, count, blowouts):
    """Calculate the biggest or smallest wins in league history.

    Arguments:
        start_year (str or None) -- the first year to check
        end_year (str or None) -- the last year to check
        playoffs (bool) -- whether or not to include playoffs
        count (int) -- how many records to include
        blowouts (bool) -- if True, return biggest wins, else return smallest

    Returns:
        resp (object) -- blowouts and avg score by year
        {
            1: {
                "year": 2018,
                "difference": 112.46,
                "winner": "Little Lebowski Urban Achievers",
                "loser": 'Laces Out!'
            },
            2: {...}
        }
    """
    async with aiohttp.ClientSession() as session:
        all_matchups = {}
        start_year = check_start_year(start_year)
        end_year = await check_end_year(end_year, session)

        for year in range(int(start_year), int(end_year) + 1):
            weeks = await number_of_weeks(year, playoffs, session)
            if weeks == 0:
                continue

            season = await load_data(year, 'mNav', session)
            matchups = await load_matchups(year, session)

            for idx, matchup in enumerate(matchups):
                matchup_id = f'{year}_{idx}'
                matchup_result = {}
                if matchup["matchupPeriodId"] > weeks:
                    break

                if is_bye_week(matchup):
                    continue

                away_dict = matchup["away"]["pointsByScoringPeriod"]
                away_score = next(iter(away_dict.values()))
                away_team_id = matchup["away"]["teamId"]

                if season["seasonId"] == year:
                    away_team_name = team_name(away_team_id, season)

                home_dict = matchup["home"]["pointsByScoringPeriod"]
                home_score = next(iter(home_dict.values()))
                home_team_id = matchup["home"]["teamId"]

                if season["seasonId"] == year:
                    home_team_name = team_name(home_team_id, season)

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

        sorted_blowouts = collections.OrderedDict(
            sorted(
                all_matchups.items(),
                key=lambda t: t[1]["difference"],
                reverse=blowouts
                )
            )

        resp = {}
        for idx, x in enumerate(list(sorted_blowouts)[0:int(count)]):
            resp[idx+1] = sorted_blowouts[x]
        return resp
