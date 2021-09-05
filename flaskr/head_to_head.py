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
            "id": team["id"]
        })
    return team_options


def results(team_id_1, team_id_2):
    data = {
        team_id_1: {
            "id": team_id_1,
            "name": "",
            "logo": "",
            "reg_wins": 0,
            "reg_ties": 0,
            "reg_points": Decimal(0.00),
            "playoff_wins": 0,
            "playoff_points": Decimal(0.00),
        },
        team_id_2: {
            "id": team_id_2,
            "name": "",
            "logo": "",
            "reg_wins": 0,
            "reg_ties": 0,
            "reg_points": Decimal(0.00),
            "playoff_wins": 0,
            "playoff_points": Decimal(0.00),
        },
        "current_streak": {
            "team": 0,
            "length": 0
        },
        "longest_streak": {
            "team": 0,
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

        for matchup in matchups:
            if matchup["matchupPeriodId"] > weeks:
                break

            if is_bye_week(matchup):
                continue

            away_details = matchup["away"]
            away_id = away_details["teamId"]
            home_details = matchup["home"]
            home_id = home_details["teamId"]
            right_matchup = compare_lists(
                [team_id_1, team_id_2],
                [away_id, home_id])
            if not right_matchup:
                continue

            # matchup be right
            away_pts = Decimal(str(away_details["totalPoints"]))
            home_pts = Decimal(str(home_details["totalPoints"]))

            data[away_id]["name"] = team_name(away_id, current_info)
            data[away_id]["logo"] = fantasy_team_logo(away_id, current_info)
            data[home_id]["name"] = team_name(home_id, current_info)
            data[home_id]["logo"] = fantasy_team_logo(home_id, current_info)

            if matchup["playoffTierType"] == "NONE":
                data[away_id]["reg_points"] += away_pts
                data[home_id]["reg_points"] += home_pts

                if away_pts > home_pts:
                    winners.append(away_id)
                    data[away_id]["reg_wins"] += 1
                elif away_pts < home_pts:
                    winners.append(home_id)
                    data[home_id]["reg_wins"] += 1
                elif away_pts == home_pts:
                    data[away_id]["reg_ties"] += 1
                    data[home_id]["reg_ties"] += 1

            elif matchup["playoffTierType"] == "WINNERS_BRACKET":
                data[away_id]["playoff_points"] += away_pts
                data[home_id]["playoff_points"] += home_pts

                if away_pts > home_pts:
                    winners.append(away_id)
                    data[away_id]["playoff_wins"] += 1
                elif away_pts < home_pts:
                    winners.append(home_id)
                    data[home_id]["playoff_wins"] += 1

    cstreak = current_streak(winners)
    lstreak = longest_streak(winners)
    data["current_streak"]["team"] = cstreak[0]
    data["current_streak"]["length"] = cstreak[1]
    data["longest_streak"]["team"] = lstreak[0]
    data["longest_streak"]["length"] = lstreak[1]

    return [
        data[team_id_1],
        data[team_id_2],
        data["current_streak"],
        data["longest_streak"]
        ]
