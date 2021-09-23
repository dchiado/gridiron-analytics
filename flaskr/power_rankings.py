from flaskr.utils import (
    is_bye_week,
    latest_season,
    load_data,
    number_of_weeks,
    team_mapping
)
import statistics
import collections
import aiohttp


def calculate_pr_score(team_obj, week):
    weights = {
        "wins": 3,
        "overall_wins": 1,
        "last_five": 1 if week >= 9 else 0,
        "points": 2,
        "consistency": 1 if week >= 4 else 0
    }

    return ((
        (weights["wins"] * team_obj["wins_rank"]) +
        (weights["overall_wins"] * team_obj["overall_wins_rank"]) +
        (weights["last_five"] * team_obj["l5_rank"]) +
        (weights["points"] * team_obj["tot_pts_rank"]) +
        (weights["consistency"] * team_obj["consistency_rank"])
    ) / sum(weights.values()))


def update_overall_wins(tm, all_week_pts):
    if 'overall_wins' not in tm:
        tm["overall_wins"] = 0
    for idx, s in enumerate(tm["scores"]):
        week_overall_wins = sorted(all_week_pts[idx + 1]).index(s)
        tm["overall_wins"] += week_overall_wins


async def current():
    async with aiohttp.ClientSession() as session:
        teams = {}
        year = await latest_season(session)

        matchups_resp = await load_data(year, 'mMatchupScore', session)
        matchups = matchups_resp["schedule"]
        current_week = matchups_resp["scoringPeriodId"]

        weeks = await number_of_weeks(year, False, session)
        if weeks == 0:
            return {"error": "No weeks in this season"}

        team_names = await team_mapping(year, session)

        all_week_pts = {}
        # loop through all matchups in the regular season
        for matchup in matchups:
            week = matchup["matchupPeriodId"]
            if week > weeks or week > current_week:
                break

            if is_bye_week(matchup):
                continue

            if week not in all_week_pts:
                all_week_pts[week] = []

            # add team's score and win/loss to teams obj
            for t in ["home", "away"]:
                t_id = matchup[t]["teamId"]
                pts = matchup[t]["totalPoints"]
                won = matchup["winner"].lower() == t
                all_week_pts[week].append(pts)
                if t_id not in teams:
                    teams[t_id] = {
                        "name": team_names[t_id],
                        "scores": [pts],
                        "games": [won]
                    }
                else:
                    teams[t_id]["scores"].append(pts)
                    teams[t_id]["games"].append(won)

        all_wins = []
        all_overall_wins = []
        all_l5 = []
        all_pts = []
        all_consistency = []

        # loop through teams object and add sum values
        # to teams object and all_ lists
        for id, tm in teams.items():
            tm["wins"] = sum(tm["games"])
            all_wins.append(tm["wins"])

            tm["l5"] = sum(tm["games"][-5:])
            all_l5.append(tm["l5"])

            tm["tot_pts"] = round(sum(tm["scores"]), 2)
            all_pts.append(tm["tot_pts"])

            tm["consistency"] = round(statistics.pstdev(tm["scores"]), 2)
            all_consistency.append(tm["consistency"])

            update_overall_wins(tm, all_week_pts)
            all_overall_wins.append(tm["overall_wins"])

        # go through again and get the rank of relevant
        # values and calculate power rankings score
        for tm in teams.values():
            tm["wins_rank"] = (
                sorted(all_wins, reverse=True).index(tm["wins"]) + 1
            )
            tm["l5_rank"] = (
                sorted(all_l5, reverse=True).index(tm["l5"]) + 1
            )
            tm["tot_pts_rank"] = (
                sorted(all_pts, reverse=True).index(tm["tot_pts"]) + 1
            )
            tm["consistency_rank"] = (
                sorted(all_consistency).index(tm["consistency"]) + 1
            )
            tm["overall_wins_rank"] = (
                sorted(
                    all_overall_wins, reverse=True
                    ).index(tm["overall_wins"]) + 1
            )

            power_ranking_score = calculate_pr_score(tm, current_week)
            tm["power_ranking_score"] = round(power_ranking_score, 2)

        # return sorted teams object
        return collections.OrderedDict(
            sorted(teams.items(), key=lambda x: x[1]['power_ranking_score'])
        )
