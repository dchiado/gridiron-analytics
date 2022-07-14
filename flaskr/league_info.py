import aiohttp
from flaskr.utils import load_data, season_status


async def summary():
    """Assemble basic league information."""
    async with aiohttp.ClientSession() as session:
        status = await season_status(session)
        year = status["season"]

        details = await load_data(year, 'mNav', session)

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
