import aiohttp
from flaskr.utils import load_data, latest_season


async def summary():
    """Assemble basic league information."""
    async with aiohttp.ClientSession() as session:
        year = await latest_season(session)

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
