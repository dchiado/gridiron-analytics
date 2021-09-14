from flaskr.utils import load_data, load_matchups, team_mapping, latest_season
from decimal import Decimal


# team with the highest score that week
def highest_score(matchups):
    high = {}
    for m in matchups:
        for t in ["home", "away"]:
            if ("score" not in high
                    or m[t]["totalPoints"] > high["score"]):
                high = {
                    "team": m[t]["teamName"],
                    "score": Decimal(str(m[t]["totalPoints"]))
                }
    return high


# team with the lowest score that week
def lowest_score(matchups):
    low = {}
    for m in matchups:
        for t in ["home", "away"]:
            if ("score" not in low
                    or m[t]["totalPoints"] < low["score"]):
                low = {
                    "team": m[t]["teamName"],
                    "score": Decimal(str(m[t]["totalPoints"]))
                }
    return low


# closest matchup of the week
def closest_win(matchups):
    closest = {}
    for m in matchups:
        diff = (Decimal(str(m["home"]["totalPoints"])) -
                Decimal(str(m["away"]["totalPoints"])))
        tie = int(diff) == 0
        if "difference" not in closest or abs(diff) < closest["difference"]:
            if m["winner"] == "HOME":
                winner = m["home"]["teamName"]
                loser = m["away"]["teamName"]
            elif m["winner"] == "AWAY":
                winner = m["away"]["teamName"]
                loser = m["home"]["teamName"]

            closest = {
                "tie": tie,
                "difference": abs(diff),
                "winner": winner,
                "loser": loser
            }
    return closest


# biggest blowout of the week
def biggest_win(matchups):
    biggest = {}
    for m in matchups:
        diff = (Decimal(str(m["home"]["totalPoints"])) -
                Decimal(str(m["away"]["totalPoints"])))
        if "difference" not in biggest or abs(diff) > biggest["difference"]:
            if m["winner"] == "HOME":
                winner = m["home"]["teamName"]
                loser = m["away"]["teamName"]
            elif m["winner"] == "AWAY":
                winner = m["away"]["teamName"]
                loser = m["home"]["teamName"]

            biggest = {
                "difference": abs(diff),
                "winner": winner,
                "loser": loser
            }
    return biggest


# lowest scoring team that won
def luckiest_win(matchups):
    all_scores = []
    luckiest = {}
    for m in matchups:
        all_scores.append(Decimal(str(m["away"]["totalPoints"])))
        all_scores.append(Decimal(str(m["home"]["totalPoints"])))
        if m["winner"] == "HOME":
            win_score = Decimal(str(m["home"]["totalPoints"]))
            winner = m["home"]["teamName"]
        elif m["winner"] == "AWAY":
            win_score = Decimal(str(m["away"]["totalPoints"]))
            winner = m["away"]["teamName"]

        if "score" not in luckiest or win_score < luckiest["score"]:
            luckiest = {
                "score": win_score,
                "team": winner,
            }

    luckiest["place"] = (
        sorted(all_scores, reverse=True).index(luckiest["score"]) + 1
    )
    return luckiest


# highest scoring team that lost
def unluckiest_loss(matchups):
    all_scores = []
    unluckiest = {}
    for m in matchups:
        all_scores.append(m["away"]["totalPoints"])
        all_scores.append(m["home"]["totalPoints"])
        if m["winner"] == "HOME":
            loss_score = m["away"]["totalPoints"]
            loser = m["away"]["teamName"]
        elif m["winner"] == "AWAY":
            loss_score = m["home"]["totalPoints"]
            loser = m["home"]["teamName"]

        if "score" not in unluckiest or loss_score > unluckiest["score"]:
            unluckiest = {
                "score": loss_score,
                "team": loser,
            }

    unluckiest["place"] = (
        sorted(all_scores, reverse=True).index(unluckiest["score"]) + 1
    )
    return unluckiest


def generate_results(matchups):
    results = []
    for matchup in matchups:
        if matchup["winner"] == "HOME":
            results.append({
                "winner": matchup["home"]["teamName"],
                "w_score": Decimal(str(matchup["home"]["totalPoints"])),
                "loser": matchup["away"]["teamName"],
                "l_score": Decimal(str(matchup["away"]["totalPoints"]))
                # TODO include team logo in results object
            })
        elif matchup["winner"] == "AWAY":
            results.append({
                "winner": matchup["away"]["teamName"],
                "w_score": Decimal(str(matchup["away"]["totalPoints"])),
                "loser": matchup["home"]["teamName"],
                "l_score": Decimal(str(matchup["home"]["totalPoints"]))
            })
        elif matchup["away"]["totalPoints"] == matchup["home"]["totalPoints"]:
            results.append({
                "tie": True,
                "winner": matchup["home"]["teamName"],
                "w_score": Decimal(str(matchup["home"]["totalPoints"])),
                "loser": matchup["away"]["teamName"],
                "l_score": Decimal(str(matchup["away"]["totalPoints"]))
            })
    return results


def generate_preview(matchups):
    preview = []
    for matchup in matchups:
        preview.append({
            "home": matchup["home"]["teamName"],
            "away": matchup["away"]["teamName"],
            # TODO include current record here
            # also h2h all time / this year
        })
    return preview


def summary():
    year = latest_season()
    team_names = team_mapping(year)
    details = load_data(year, 'mNav')
    all_matchups = load_matchups(year)
    for matchup in all_matchups:
        matchup["away"]["teamName"] = team_names[matchup["away"]["teamId"]]
        matchup["home"]["teamName"] = team_names[matchup["home"]["teamId"]]

    week = details["status"]["currentMatchupPeriod"] - 1
    response = {
        "week": week,
        "next_week": week + 1
    }

    if week < 1:
        response["results"] = {"error": "NoMatchups"}
    else:
        week_matchups = [
            m for m in all_matchups if m["matchupPeriodId"] == week
            ]

        results = generate_results(week_matchups)

        high_score = highest_score(week_matchups)
        low_score = lowest_score(week_matchups)

        closest = closest_win(week_matchups)
        biggest = biggest_win(week_matchups)

        luckiest = luckiest_win(week_matchups)
        unluckiest = unluckiest_loss(week_matchups)

        response["results"] = results
        response["superlatives"] = {
            "high": high_score,
            "low": low_score,
            "closest": closest,
            "blowout": biggest,
            "luckiest": luckiest,
            "unluckiest": unluckiest
        }

    next_week_matchups = [
        m for m in all_matchups if m["matchupPeriodId"] == week + 1
        ]
    preview = generate_preview(next_week_matchups)
    response["preview"] = preview

    return response
