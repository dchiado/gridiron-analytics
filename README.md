# GridironAnalytics
This program compiles data on an ESPN fantasy football league using python and the public ESPN API. 

## Prerequisites
This program requires Python 3, which can be obtained [here](https://www.python.org/downloads).

## Use
- Obtain your league ID from any page in your league (`leagueId=166975`)
- export flask environment variables
```
export FLASK_APP=flaskr
export FLASK_ENV=development
```
- Run the app with:
```
flask run
```
- The web app will be available at `http://127.0.0.1:5000`

Alternatively, you can run them from the command line like:
```
$ python3 -c 'from flaskr import matchups; print(matchups.results(2009, 2011, False, 5, True))'
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