from flaskr.utils import load_data, latest_season


def summary():
    year = latest_season()

    details = load_data(year, 'mNav')

    name = details["settings"]["name"]
    est = details["status"]["previousSeasons"][0]
    teams = details["status"]["teamsJoined"]
    week = details["status"]["currentMatchupPeriod"]

    return {
        "name": name,
        "established": est,
        "teams": teams,
        "year": year,
        "week": week
    }