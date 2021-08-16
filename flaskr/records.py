from flaskr.utils import LoadData, LatestSeason
from flaskr.globals import LEAGUE_ID, FIRST_SEASON

def list(start_year, end_year):
    all_records = {}
    start_year = start_year or FIRST_SEASON
    end_year = end_year or LatestSeason(LEAGUE_ID)

    for year in range(int(start_year), int(end_year) + 1):
        teams = LoadData(year, LEAGUE_ID, 'mTeam')["teams"]
        owners = LoadData(year, LEAGUE_ID, 'mNav')["members"]

        for team in teams:
            owner_id = team["primaryOwner"]
            team_info = next((owner for owner in owners if owner["id"] == owner_id))
            lname = team_info["lastName"].capitalize()
            owner = f'{team_info["firstName"].capitalize()} {lname}'

            season_wins = team["record"]["overall"]["wins"]
            season_losses = team["record"]["overall"]["losses"]
            season_ties = team["record"]["overall"]["ties"]
            season_pf = round(team["record"]["overall"]["pointsFor"], 2)
            season_pa = round(team["record"]["overall"]["pointsAgainst"], 2)

            if lname in all_records:
                all_records[lname]["wins"] += season_wins
                all_records[lname]["losses"] += season_losses
                all_records[lname]["ties"] += season_ties
                all_records[lname]["pointsFor"] += season_pf
                all_records[lname]["pointsAgainst"] += season_pa
            else:
                all_records[lname] = {
                    "id": team["id"],
                    "owner": owner,
                    "wins": season_wins,
                    "losses": season_losses,
                    "ties": season_ties,
                    "pointsFor": season_pf,
                    "pointsAgainst": season_pa
                }

    return all_records