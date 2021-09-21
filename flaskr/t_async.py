from flaskr.utils import load_data
import datetime
import time
import requests
import aiohttp
import asyncio
import json
import os
from aiohttp import ClientSession


start_time = time.time()


async def call_api():
    async with aiohttp.ClientSession() as session:
        for n in range(1, 100):
            print(n)
            await load_data(2020, 'mMatchup', session)


asyncio.run(call_api())
print("--- %s seconds ---" % (time.time() - start_time))
