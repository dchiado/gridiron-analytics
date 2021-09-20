from flaskr.utils import (
    is_bye_week,
    latest_season,
    load_matchups,
    number_of_weeks,
    team_mapping
)
import statistics


# Wins rank			    x	3
# Overall wins rank		x	1
# Last 5 rank			x	1
# Consistency rank		x	1
# Total points rank		x	1.5
# Roster strength rank	x	1
def current():
    teams = {}
    year = latest_season()
    matchups = load_matchups(year)
    weeks = number_of_weeks(year, False)
    if weeks == 0:
        return {"error": "No weeks in this season"}

    matchups = load_matchups(year)
    team_names = team_mapping(year)

    # loop through all matchups in the regular season
    for matchup in matchups:
        if matchup["matchupPeriodId"] > weeks:
            break

        if is_bye_week(matchup):
            continue

        # add team's score and win/loss to teams obj
        for t in ["home", "away"]:
            t_id = matchup[t]["teamId"]
            pts = matchup[t]["totalPoints"]
            won = matchup["winner"].lower() == t
            if t_id not in teams:
                teams[t_id] = {
                    "scores": [pts],
                    "games": [won]
                }
            else:
                teams[t_id]["scores"].append(pts)
                teams[t_id]["games"].append(won)

    all_wins = []
    all_l5 = []
    all_pts = []
    all_consistency = []

    # loop through teams object and add sum values
    # to teams object and all_ lists
    for tm in teams.values():
        wins = sum(tm["games"])
        tm["wins"] = wins
        all_wins.append(wins)

        l5 = sum(tm["games"][-5:])
        tm["l5"] = l5
        all_l5.append(l5)

        tot_pts = sum(tm["scores"])
        tm["tot_pts"] = tot_pts
        all_pts.append(tot_pts)

        stdev = statistics.pstdev(tm["scores"])
        tm["consistency"] = stdev
        all_consistency.append(stdev)

    # go through again and get the rank of relevant
    # values and calculate power rankings score
    for id, tm in teams.items():
        wins_rank = sorted(all_wins, reverse=True).index(tm["wins"]) + 1
        l5_rank = sorted(all_l5, reverse=True).index(tm["l5"]) + 1
        tot_pts_rank = sorted(all_pts, reverse=True).index(tm["tot_pts"]) + 1
        consistency_rank = sorted(all_consistency).index(tm["consistency"]) + 1

        power_ranking_score = (
            (3 * wins_rank) +
            (1 * l5_rank) +
            (1.5 * tot_pts_rank) +
            (1 * consistency_rank)
        ) / 6.5

        print(team_names[id])
        print(power_ranking_score)
