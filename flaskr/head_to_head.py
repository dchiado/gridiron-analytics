from flaskr.utils import (
    is_bye_week,
    latest_season,
    load_matchups,
    number_of_weeks,
    compare_lists,
    load_data,
    team_name,
    fantasy_team_logo,
    current_streak,
    longest_streak
)
from flaskr.globals import FIRST_SEASON
from decimal import Decimal


def options():
    year = latest_season()
    teams = load_data(year, 'mNav')["teams"]
    team_options = []
    for team in teams:
        team_options.append({
            "name": team["location"] + " " + team["nickname"],
            "owner_id": team["owners"][0]
        })
    return team_options


def all_time(owner_id_1, owner_id_2):
    # Need to use owner id because some ids stayed
    # the same through multiple owners
    data = {
        owner_id_1: {
            "owner_id": owner_id_1,
            "name": "",
            "logo": "",
            "reg_wins": 0,
            "reg_ties": 0,
            "reg_points": Decimal(0.00),
            "playoff_wins": 0,
            "playoff_points": Decimal(0.00),
        },
        owner_id_2: {
            "owner_id": owner_id_2,
            "name": "",
            "logo": "",
            "reg_wins": 0,
            "reg_ties": 0,
            "reg_points": Decimal(0.00),
            "playoff_wins": 0,
            "playoff_points": Decimal(0.00),
        },
        "current_streak": {
            "owner_id": 0,
            "length": 0
        },
        "longest_streak": {
            "owner_id": 0,
            "length": 0
        },
    }

    end_year = latest_season()
    current_info = load_data(end_year, 'mNav')
    winners = []

    for year in range(FIRST_SEASON, end_year + 1):
        weeks = number_of_weeks(year, True)
        if weeks == 0:
            continue

        matchups = load_matchups(year)
        team_owner_mapping = load_data(year, 'mNav')["teams"]

        for matchup in matchups:
            if matchup["matchupPeriodId"] > weeks:
                break

            if is_bye_week(matchup):
                continue

            away_details = matchup["away"]
            away_team_id = away_details["teamId"]
            away_owner_id = next(
                item for item in team_owner_mapping
                if item["id"] == away_team_id
                )["owners"][0]

            home_details = matchup["home"]
            home_team_id = home_details["teamId"]
            home_owner_id = next(
                item for item in team_owner_mapping
                if item["id"] == home_team_id
                )["owners"][0]

            right_teams = compare_lists(
                [owner_id_1, owner_id_2],
                [away_owner_id, home_owner_id])
            if not right_teams:
                continue

            # matchup be right
            away_pts = Decimal(str(away_details["totalPoints"]))
            home_pts = Decimal(str(home_details["totalPoints"]))

            data[away_owner_id]["name"] = team_name(away_team_id, current_info)
            data[away_owner_id]["logo"] = fantasy_team_logo(
                away_team_id, current_info
                )

            data[home_owner_id]["name"] = team_name(home_team_id, current_info)
            data[home_owner_id]["logo"] = fantasy_team_logo(
                home_team_id, current_info
                )

            if matchup["playoffTierType"] == "NONE":
                data[away_owner_id]["reg_points"] += away_pts
                data[home_owner_id]["reg_points"] += home_pts

                if away_pts > home_pts:
                    winners.append(away_owner_id)
                    data[away_owner_id]["reg_wins"] += 1
                elif away_pts < home_pts:
                    winners.append(home_owner_id)
                    data[home_owner_id]["reg_wins"] += 1
                elif away_pts == home_pts:
                    data[away_owner_id]["reg_ties"] += 1
                    data[home_owner_id]["reg_ties"] += 1

            elif matchup["playoffTierType"] == "WINNERS_BRACKET":
                data[away_owner_id]["playoff_points"] += away_pts
                data[home_owner_id]["playoff_points"] += home_pts

                if away_pts > home_pts:
                    winners.append(away_owner_id)
                    data[away_owner_id]["playoff_wins"] += 1
                elif away_pts < home_pts:
                    winners.append(home_owner_id)
                    data[home_owner_id]["playoff_wins"] += 1

    cstreak = current_streak(winners)
    lstreak = longest_streak(winners)
    data["current_streak"]["team"] = cstreak[0]
    data["current_streak"]["length"] = cstreak[1]
    data["longest_streak"]["team"] = lstreak[0]
    data["longest_streak"]["length"] = lstreak[1]

    return [
        data[owner_id_1],
        data[owner_id_2],
        data["current_streak"],
        data["longest_streak"]
        ]


def record(owner_id_1, owner_id_2):
    # Need to use owner id because some ids stayed
    # the same through multiple owners
    data = {
        owner_id_1: {
            "owner_id": owner_id_1,
            "wins": 0,
        },
        owner_id_2: {
            "owner_id": owner_id_2,
            "wins": 0,
        },
    }

    end_year = latest_season()
    current_info = load_data(end_year, 'mNav')

    for year in range(FIRST_SEASON, end_year + 1):
        weeks = number_of_weeks(year, True)
        if weeks == 0:
            continue

        matchups = load_matchups(year)
        team_owner_mapping = load_data(year, 'mNav')["teams"]

        for matchup in matchups:
            if matchup["matchupPeriodId"] > weeks:
                break

            if is_bye_week(matchup):
                continue

            away_details = matchup["away"]
            away_team_id = away_details["teamId"]
            away_owner_id = next(
                item for item in team_owner_mapping
                if item["id"] == away_team_id
                )["owners"][0]

            home_details = matchup["home"]
            home_team_id = home_details["teamId"]
            home_owner_id = next(
                item for item in team_owner_mapping
                if item["id"] == home_team_id
                )["owners"][0]

            right_teams = compare_lists(
                [owner_id_1, owner_id_2],
                [away_owner_id, home_owner_id])
            if not right_teams:
                continue

            # matchup be right
            if matchup["playoffTierType"] == "NONE" or matchup["playoffTierType"] == "WINNERS_BRACKET":
                if matchup["winner"] == "AWAY":
                    data[away_owner_id]["wins"] += 1
                elif matchup["winner"] == "HOME":
                    data[home_owner_id]["wins"] += 1
    return [
        data[owner_id_1],
        data[owner_id_2],
        ]
