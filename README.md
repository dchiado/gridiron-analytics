# gridiron-analytics
This program compiles data on an ESPN fantasy football league using the public ESPN API.
The app uses python scripts to retrieve and organize the data and is built on [flask](https://flask.palletsprojects.com/en/2.0.x/).

## Prerequisites
1. Python 3 is required, which can be obtained [here](https://www.python.org/downloads).
2. Set up your virtual environment. If you name it something other than `env`, make sure to gitignore that dir.
```
python3 -m venv env
```
3. Activate your virtual environment.
```
source env/bin/activate
```
4. Install all dependencies:
```
pip install -r requirements.txt
```
5. Export flask environment variables
```
export FLASK_APP=flaskr
export FLASK_ENV=development
```

## Use
- Obtain your league ID from the URL of any page in your league (`https://fantasy.espn.com/...leagueId=166975`). Add the id to the LEAGUE_ID variable in `flaskr/globals.py` if not already there.
- Run the app with:
```
flask run
```
- The web app will be available at `http://127.0.0.1:5000`

## Linting
flake8 is used for linting and code style. Configuration for the linter is stored in `.flake8`. To run the linter just run `flake8` from the project root. 

## Testing
The `pytest` module is used for testing. All tests are stored under the `tests/` dir in the project root. To run the tests just run:
```
python -m pytest
```

## ESPN API
ESPN has a public API for fantasy leagues that are marked as "publicly accessible". For these,
there is no need for an auth token or key and the API can be accessed with just the league ID.

### Endpoints
The endpoints are not well documented, so there are sample responses inside the `api` directory.
This data is not live but is just for viewing the response structure.

For recent seasons, the endpoint looks like this where endpoint is the name of the json file in
that directory, such as `mDraftDetail`:

`http://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?&view={endpoint}`

For older seasons, the endpoint looks like this:

`https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}?seasonId={year}&view={endpoint}`

## UI Components
Material Design Lite is used for building frontend component. Components, examples, and other
documentation can be found [here](https://getmdl.io/components/index.html). 