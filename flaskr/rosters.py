import os
from utils import load_data
from dotenv import load_dotenv

load_dotenv()

league_id = os.getenv('LEAGUE_ID')
year = 2020
next_year_rounds = 16

rosters = load_data(year, 'mRoster')
draft = load_data(year, 'mDraftDetail')
teams = load_data(year, 'mTeam')

all_rosters = []

for team in teams["teams"]:
    team_roster_details = {}
    team_name = str(team["location"] + " " + str(team["nickname"]))
    team_roster_details["team_name"] = team_name
    team_roster_details["players"] = []

    team_id = team["id"]
    for roster in rosters["teams"]:
        if roster["id"] == team_id:
            team_roster = roster["roster"]
            break

    for player in team_roster["entries"]:
        player_details = {}

        draft_round = 'FA'
        player_id = player["playerPoolEntry"]["player"]["id"]

        player_details["name"] = (
            player["playerPoolEntry"]["player"]["fullName"]
        )
        player_details["acq_type"] = player["acquisitionType"]

        for pick in draft["draftDetail"]["picks"]:
            if pick["playerId"] == player_id:
                draft_round = pick["roundId"]
                break

        if draft_round in (1, 2):
            player_details["keeper_round"] = 1
        elif draft_round == 'FA':
            player_details["keeper_round"] = next_year_rounds - 1
        else:
            player_details["keeper_round"] = draft_round - 2

        team_roster_details["players"].append(player_details)

    all_rosters.append(team_roster_details)


print("Player, Acquired, Drafted in, Can be kept in")

for team in all_rosters:
    print()
    print(team["team_name"])
    print()
    for player in team["players"]:
        print(
            player["name"] + ", " + (
                player["acq_type"] + ", " + (
                    str(player["keeper_round"])
                )
            )
        )
