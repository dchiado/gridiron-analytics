from flaskr.utils import LoadData, LatestSeason
from flaskr.globals import LEAGUE_ID, FIRST_SEASON

def list(start_year, end_year):
    all_records = {
        "seasons": [],
        "teams": {}
    }
    start_year = start_year or FIRST_SEASON
    end_year = end_year or LatestSeason(LEAGUE_ID)

    for year in range(int(start_year), int(end_year) + 1):
        all_records["seasons"].append(year)
        team_details = LoadData(year, LEAGUE_ID, 'mTeam')
        teams = team_details["teams"]
        owners = team_details["members"]

        for team in teams:
            owner_id = team["primaryOwner"]
            team_info = next((owner for owner in owners if owner["id"] == owner_id))
            fname = team_info["firstName"].strip().capitalize()
            lname = team_info["lastName"].strip().capitalize()
            owner = f'{fname} {lname}'

            season_wins = team["record"]["overall"]["wins"]
            season_losses = team["record"]["overall"]["losses"]
            season_ties = team["record"]["overall"]["ties"]
            season_record = f'{season_wins}-{season_losses}-{season_ties}'
            season_pf = int(team["record"]["overall"]["pointsFor"])
            season_pa = int(team["record"]["overall"]["pointsAgainst"])

            if owner in all_records["teams"]:
                obj = all_records["teams"][owner]
                obj["seasons"][year] = {
                    "record": season_record
                }
                obj["total"]["wins"] += season_wins
                obj["total"]["losses"] += season_losses
                obj["total"]["ties"] += season_ties
                obj["total"]["pointsFor"] += season_pf
                obj["total"]["pointsAgainst"] += season_pa
            else:
                all_records["teams"][owner] = {
                    "seasons": {
                        year: {
                            "record": season_record
                        }
                    },
                    "total": {
                        "wins": season_wins,
                        "losses": season_losses,
                        "ties": season_ties,
                        "pointsFor": season_pf,
                        "pointsAgainst": season_pa
                    }
                }

    return all_records