import aiohttp
from flaskr.utils import load_data, latest_season, win_pct
from flaskr.globals import FIRST_SEASON


async def list():
    """Calculate league standings by year and overall for all years.

    Returns:
        all_records (object) -- blowouts and avg score by year
        {
            "seasons": [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
                        2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],
            "teams": {
                "Joe Blow": {
                    "seasons": {
                        2005: {
                            "record": "8-7-0",
                            "reg_season_champ": False,
                            "playoff_champ": False,
                            "toilet_bowl": False
                        },
                        2006: {...}
                    },
                    "total": {
                        "wins": 113,
                        "losses": 108,
                        "ties": 1,
                        "winPct":
                        "51.13%",
                        "pointsFor": 22156,
                        "pointsAgainst": 21522
                    }
                },
                "Pat Davidson": {...}
            }
        }
    """
    async with aiohttp.ClientSession() as session:
        all_records = {
            "seasons": [],
            "teams": {}
        }
        start_year = FIRST_SEASON
        end_year = await latest_season(session)

        for year in range(int(start_year), int(end_year) + 1):
            team_details = await load_data(year, 'mTeam', session)
            if team_details["status"]["currentMatchupPeriod"] == 1:
                continue

            all_records["seasons"].append(year)
            teams = team_details["teams"]
            owners = team_details["members"]

            for team in teams:
                record = team["record"]["overall"]
                reg_season_place = team["playoffSeed"]
                playoff_place = team["rankCalculatedFinal"]
                total_teams = team_details["status"]["teamsJoined"]

                owner_id = team["primaryOwner"]
                team_info = next(
                    (owner for owner in owners if owner["id"] == owner_id)
                    )
                fname = team_info["firstName"].strip().capitalize()
                lname = team_info["lastName"].strip().capitalize()
                owner = f'{fname} {lname}'

                season_wins = record["wins"]
                season_losses = record["losses"]
                season_ties = record["ties"]
                season_record = f'{season_wins}-{season_losses}-{season_ties}'
                season_pf = int(record["pointsFor"])
                season_pa = int(record["pointsAgainst"])

                emoji = ''
                poop = " \U0001F4A9"
                trophy = " \U0001F3C6"
                medal = " \U0001F3C5"

                if reg_season_place == total_teams:
                    emoji = poop
                elif playoff_place == 1 and reg_season_place == 1:
                    emoji = trophy + medal
                elif playoff_place == 1:
                    emoji = trophy
                elif reg_season_place == 1:
                    emoji = medal

                season_summary = {
                    "record": season_record + emoji,
                    "reg_season_champ": reg_season_place == 1,
                    "playoff_champ": playoff_place == 1,
                    "toilet_bowl": reg_season_place == total_teams
                }

                if owner in all_records["teams"]:
                    obj = all_records["teams"][owner]
                    obj["seasons"][year] = season_summary

                    new_wins = obj["total"]["wins"] + season_wins
                    new_losses = obj["total"]["losses"] + season_losses
                    new_ties = obj["total"]["ties"] + season_ties
                    new_win_pct = win_pct(new_wins, new_losses)

                    obj["total"]["wins"] = new_wins
                    obj["total"]["losses"] = new_losses
                    obj["total"]["ties"] = new_ties
                    obj["total"]["winPct"] = new_win_pct
                    obj["total"]["pointsFor"] += season_pf
                    obj["total"]["pointsAgainst"] += season_pa
                else:
                    all_records["teams"][owner] = {
                        "seasons": {
                            year: season_summary
                        },
                        "total": {
                            "wins": season_wins,
                            "losses": season_losses,
                            "ties": season_ties,
                            "winPct": win_pct(season_wins, season_losses),
                            "pointsFor": season_pf,
                            "pointsAgainst": season_pa
                        }
                    }

        return all_records
