from flaskr.utils import load_data, latest_season, load_matchups, team_name, team_mapping


def highest_score(matchups):
    high = {}
    for m in matchups:
        for t in ["home", "away"]:
            if ("totalPoints" not in high
                    or m[t]["totalPoints"] > high["totalPoints"]):
                high = m[t]
    return high


def lowest_score(matchups):
    low = {}
    for m in matchups:
        for t in ["home", "away"]:
            if ("totalPoints" not in low
                    or m[t]["totalPoints"] < low["totalPoints"]):
                low = m[t]
    return low


def closest_win(matchups):
    closest = {}
    for m in matchups:
        diff = abs(m["home"]["totalPoints"] - m["away"]["totalPoints"])
        tie = int(diff) == 0
        if "difference" not in closest or diff < closest["difference"]:
            if m["winner"] == "HOME":
                winner = m["home"]["teamId"]
                loser = m["away"]["teamId"]
            elif m["winner"] == "AWAY":
                winner = m["away"]["teamId"]
                loser = m["home"]["teamId"]

            closest = {
                "tie": tie,
                "difference": diff,
                "winner": winner,
                "loser": loser
            }
    return closest


def biggest_win(matchups):
    biggest = {}
    for m in matchups:
        diff = abs(m["home"]["totalPoints"] - m["away"]["totalPoints"])
        if "difference" not in biggest or diff > biggest["difference"]:
            if m["winner"] == "HOME":
                winner = m["home"]["teamId"]
                loser = m["away"]["teamId"]
            elif m["winner"] == "AWAY":
                winner = m["away"]["teamId"]
                loser = m["home"]["teamId"]

            biggest = {
                "difference": diff,
                "winner": winner,
                "loser": loser
            }
    return biggest


def luckiest_win(matchups):  # lowest score that won
    all_scores = []
    luckiest = {}
    for m in matchups:
        all_scores.append(m["away"]["totalPoints"])
        all_scores.append(m["home"]["totalPoints"])
        if m["winner"] == "HOME":
            win_score = m["home"]["totalPoints"]
            winner = m["home"]["teamId"]
        elif m["winner"] == "AWAY":
            win_score = m["away"]["totalPoints"]
            winner = m["away"]["teamId"]

        if "win_score" not in luckiest or win_score < luckiest["win_score"]:
            luckiest = {
                "score": win_score,
                "winner": winner,
            }

    luckiest["place"] = (
        sorted(all_scores, reverse=True).index(luckiest["score"]) + 1
    )
    return luckiest


def unluckiest_loss(matchups):  # highest score that lost
    all_scores = []
    unluckiest = {}
    for m in matchups:
        all_scores.append(m["away"]["totalPoints"])
        all_scores.append(m["home"]["totalPoints"])
        if m["winner"] == "HOME":
            loss_score = m["away"]["totalPoints"]
            loser = m["away"]["teamId"]
        elif m["winner"] == "AWAY":
            loss_score = m["home"]["totalPoints"]
            loser = m["home"]["teamId"]

        if "score" not in unluckiest or loss_score > unluckiest["score"]:
            unluckiest = {
                "score": loss_score,
                "loser": loser,
            }

    unluckiest["place"] = (
        sorted(all_scores, reverse=True).index(unluckiest["score"]) + 1
    )
    return unluckiest


def summary():
    # year = latest_season()
    year = 2020
    team_names = team_mapping(year)
    details = load_data(year, 'mNav')
    week = details["status"]["currentMatchupPeriod"]
    week = 9
    if week == 1:
        print('come back later')
        return

    all_matchups = load_matchups(year)
    # print(all_matchups)
    week_matchups = [m for m in all_matchups if m["matchupPeriodId"] == week]

    high_score = highest_score(week_matchups)
    high_team = team_names[high_score["teamId"]]
    low_score = lowest_score(week_matchups)
    low_team = team_names[low_score["teamId"]]

    print('high', high_team, high_score["totalPoints"])
    print('low', low_team, low_score["totalPoints"])

    closest = closest_win(week_matchups)
    print('closest', closest)
    biggest = biggest_win(week_matchups)
    print('biggest', biggest)

    luckiest = luckiest_win(week_matchups)
    print('luckiest', luckiest)
    unluckiest = unluckiest_loss(week_matchups)
    print('unluckiest', unluckiest)

# You had who and still lost -- Josh Allen got 37.1 from Will Fuller V but it wasn’t enough

