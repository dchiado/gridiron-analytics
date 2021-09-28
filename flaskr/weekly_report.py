import aiohttp
import operator
from flaskr.utils import (
    fantasy_team_logo,
    is_bye_week,
    latest_season,
    load_data,
    load_matchups,
    load_transactions,
    player_info,
    team_mapping
)
from flaskr import power_rankings
from decimal import Decimal


# team with the highest score that week
def highest_score(matchups):
    """Find team with highest score among all matchups."""
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
    """Find team with lowest score among all matchups."""
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
    """Find team with closest win among all matchups."""
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
    """Find team with biggest win among all matchups."""
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
    """Find team with lowest score but still won among all matchups."""
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
    """Find team with highest score but still lost among all matchups."""
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


def generate_results(matchups, teams):
    """Assemble results list given all matchups.

    Arguments:
        matchups (object) -- multiple matches from mMatchupScore api

    Returns:
        results (list) -- list of summarized matchups
        [
            {
                "winner": "Fantasy Football Team",
                "w_score": 155.62,
                "loser": "Gruden Says",
                "l_score": 144.14
            },
            {...}
        ]
    """
    results = []
    for matchup in matchups:
        if matchup["winner"] == "HOME":
            results.append({
                "winner": matchup["home"]["teamName"],
                "w_score": Decimal(str(matchup["home"]["totalPoints"])),
                "w_logo": fantasy_team_logo(matchup["home"]["teamId"], teams),
                "loser": matchup["away"]["teamName"],
                "l_score": Decimal(str(matchup["away"]["totalPoints"])),
                "l_logo": fantasy_team_logo(matchup["away"]["teamId"], teams)
            })
        elif matchup["winner"] == "AWAY":
            results.append({
                "winner": matchup["away"]["teamName"],
                "w_score": Decimal(str(matchup["away"]["totalPoints"])),
                "w_logo": fantasy_team_logo(matchup["away"]["teamId"], teams),
                "loser": matchup["home"]["teamName"],
                "l_score": Decimal(str(matchup["home"]["totalPoints"])),
                "l_logo": fantasy_team_logo(matchup["home"]["teamId"], teams)
            })
        elif matchup["away"]["totalPoints"] == matchup["home"]["totalPoints"]:
            results.append({
                "tie": True,
                "winner": matchup["home"]["teamName"],
                "w_score": Decimal(str(matchup["home"]["totalPoints"])),
                "w_logo": fantasy_team_logo(matchup["home"]["teamId"], teams),
                "loser": matchup["away"]["teamName"],
                "l_score": Decimal(str(matchup["away"]["totalPoints"])),
                "l_logo": fantasy_team_logo(matchup["away"]["teamId"], teams)
            })
    return results


def generate_preview(matchups, teams, prs):
    """Assemble preview list given all next week matchups.

    Arguments:
        matchups (object) -- multiple matches from mMatchupScore api
        teams (object) -- multiple teams from mTeams api
        prs (object) -- current power rankings object

    Returns:
        preview (list) -- list of summarized matchups for next week
        [
            {
                "home": "Fantasy Football Team",
                "home_record": "0-2,
                "away": "Gruden Says",
                "away_record": "1-1"
            },
            {...}
        ]
    """
    preview = []
    for matchup in matchups:
        m = {}
        ids = []
        for t in ["home", "away"]:
            team = next(
                tm for tm in teams["teams"] if tm["id"] == matchup[t]["teamId"]
            )
            rec = team["record"]["overall"]
            record = str(rec["wins"]) + '-' + str(rec["losses"])
            m[t] = matchup[t]["teamName"]
            m[t + "_logo"] = fantasy_team_logo(matchup[t]["teamId"], teams)
            m[t + "_record"] = record
            m[t + "_pr"] = list(prs).index(matchup[t]["teamId"]) + 1
            m["game_of_week"] = None
            ids.append(team["owners"][0])

        # this would include h2h record but until i get async calls
        # working it just takes to long to load the report page
        # rec = head_to_head.record(ids[0], ids[1])
        preview.append(m)

    # matchup with lowest total PRs is game of week
    sorted(
        preview, key=lambda x: x["home_pr"] + x["away_pr"]
    )[0]["game_of_week"] = True

    return preview


def winning_bids(transactions):
    """Get FAAB bids that won"""
    return [t for t in transactions if
            t["type"] == "WAIVER" and t["status"] == "EXECUTED"]


def biggest_faab_bid(transactions, team_names, player_names):
    """Get highest FAAB bid"""
    w_bids = winning_bids(transactions)
    bid = sorted(w_bids, key=lambda x: x["bidAmount"], reverse=True)[0]
    bid["teamName"] = team_names[bid["teamId"]]
    bid["playerName"] = next(
        p["player"]["fullName"] for p in player_names if
        p["id"] == bid["items"][0]["playerId"]
    )
    return bid


def best_worst_bids(transactions, team_names, player_names, overpay=False):
    """Find best (most efficient) or worst (biggest overpay) FAAB bids.

    The winning_bid and losing_bid objects in the response are objects from
    the mTransactions2 api endpoint.

    Arguments:
        transactions (object) -- all transactions of the week
        team_names (object) -- mapping of teamId to teamName
        player_names (object) -- mapping of playerId to playerName
        overpay (bool) -- return biggest overpay if True, else the best bid

    Returns:
        bid (object) -- list of summarized matchups for next week
        {
            "teamName": "Fantasy Football Team",
            "playerName": "Shonn Greene",
            "diff": 51,
            "winning_bid": {...},
            "losing_bid": {...}
        }
    """
    # check > if overpay=True, else check <
    if overpay:
        compare = operator.gt
    else:
        compare = operator.lt

    w_bids = winning_bids(transactions)
    bid = {}

    for w in w_bids:
        l_bids = [
            t for t in transactions if t["type"] == "WAIVER" and
            t["status"] == "FAILED_INVALIDPLAYERSOURCE" and
            t["items"][0]["playerId"] == w["items"][0]["playerId"]
        ]
        if len(l_bids) > 0:
            next_highest = sorted(
                l_bids, key=lambda x: x["bidAmount"], reverse=True
            )[0]
        else:
            next_highest = {"bidAmount": 0, "teamId": None}

        diff = w["bidAmount"] - next_highest["bidAmount"]
        if 'diff' not in bid or compare(diff, bid["diff"]):
            bid = {
                "diff": diff,
                "winning_bid": w,
                "losing_bid": next_highest
            }

    bid["teamName"] = team_names[bid["winning_bid"]["teamId"]]
    bid["playerName"] = next(
        p["player"]["fullName"] for p in player_names if
        p["id"] == bid["winning_bid"]["items"][0]["playerId"]
    )

    return bid


async def summary():
    """Assemble summary of weekly report and next week preview.

    Returns:
        response (object) -- list of weekly recap, superlatives, and preview
        {
            "week": 2,
            "next_week": 3,
            "results": [
                {
                    "winner": "Gridiron Shotgunner",
                    "w_score": 127.88,
                    "loser": "Gordon and The Mighty Ducks",
                    "l_score": 118.34
                },
                {...}
            ],
            "superlatives": {
                "high": {
                    "team": "IC Light",
                    "score": 166.86
                },
                "low": {...},
                "closest": {...},
                "blowout": {...},
                "luckiest": {...},
                "unluckiest": {...},
                "high_bid": {...},
                "overpay_bid": {...},
                "efficient_bid": {...}
            },
            "preview": [
                {
                    "home": ". Giggity",
                    "home_record": "0-2",
                    "away": "Gordon and The Mighty Ducks",
                    "away_record": "1-1"
                },
                {...}
            ],
            "power_rankings": {...}
        }
    """
    async with aiohttp.ClientSession() as session:
        year = await latest_season(session)
        team_names = await team_mapping(year, session)
        player_names = await player_info(year, session)
        details = await load_data(year, 'mTeam', session)

        all_matchups = await load_matchups(year, session)
        for matchup in all_matchups:
            if is_bye_week(matchup):
                break
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

            results = generate_results(week_matchups, details)

            high_score = highest_score(week_matchups)
            low_score = lowest_score(week_matchups)

            closest = closest_win(week_matchups)
            biggest = biggest_win(week_matchups)

            luckiest = luckiest_win(week_matchups)
            unluckiest = unluckiest_loss(week_matchups)

            week_transactions = await load_transactions(year,
                                                        session,
                                                        week=week)
            high_bid = biggest_faab_bid(week_transactions,
                                        team_names,
                                        player_names)
            overpay_bid = best_worst_bids(week_transactions,
                                          team_names,
                                          player_names, overpay=True)
            efficient_bid = best_worst_bids(week_transactions,
                                            team_names,
                                            player_names, overpay=False)

            response["results"] = results
            response["superlatives"] = {
                "high": high_score,
                "low": low_score,
                "closest": closest,
                "blowout": biggest,
                "luckiest": luckiest,
                "unluckiest": unluckiest,
                "high_bid": high_bid,
                "overpay_bid": overpay_bid,
                "efficient_bid": efficient_bid
            }

        prs = await power_rankings.current()
        response["power_rankings"] = prs

        next_week_matchups = [
            m for m in all_matchups if m["matchupPeriodId"] == week + 1
        ]
        preview = generate_preview(next_week_matchups, details, prs)
        response["preview"] = preview

        return response
