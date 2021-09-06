from flaskr import utils


# TODO mock load_matchup


def test_is_bye_week():
    matchup1 = {
      "away": {
        "cumulativeScore": {
          "losses": 0,
          "ties": 0,
          "wins": 0
        },
        "teamId": 17,
        "totalPoints": 149.4
      },
      "home": {
        "cumulativeScore": {
          "losses": 0,
          "ties": 0,
          "wins": 0
        },
        "teamId": 20,
        "totalPoints": 148.52
      }
    }
    matchup2 = {
      "home": {
        "cumulativeScore": {
          "losses": 0,
          "ties": 0,
          "wins": 0
        },
        "teamId": 20,
        "totalPoints": 148.52
      }
    }
    matchup3 = {}
    assert utils.is_bye_week(matchup1) is False
    assert utils.is_bye_week(matchup2) is True
    assert utils.is_bye_week(matchup3) is True


def test_team_name():
    season = {
        "teams": [
            {
                "id": 1,
                "location": "Myrtle Beach",
                "nickname": "Mermen"
            }
        ]
    }
    assert utils.team_name(1, season) == "Myrtle Beach Mermen"
    assert utils.team_name(2, season) is None


def test_fantasy_team_logo():
    season = {
        "teams": [
            {
                "id": 1,
                "logo": "www.abc.com"
            }
        ]
    }
    assert utils.fantasy_team_logo(1, season) == "www.abc.com"
    assert utils.fantasy_team_logo(2, season) is None


def test_headshot():
    assert utils.headshot(456) == (
        "https://a.espncdn.com/i/headshots/nfl/players/full/456.png"
        )


def test_team_logo():
    assert True is True
    # TODO mock team_abbreviation


def test_team_abbreviation():
    assert utils.team_abbreviation("Steelers") == "pit"


def test_active_teams():
    mTeam = {
        "teams": [
            {
                "id": 1
            },
            {
                "id": 6
            },
            {
                "id": 18
            }
        ]
    }
    assert utils.active_teams(mTeam) == [1, 6, 18]


def test_win_pct():
    assert utils.win_pct(2, 3) == '40.0%'


def test_compare_lists():
    assert utils.compare_lists([1, 2], [1, 2]) is True
    assert utils.compare_lists([1, 2], [2, 1]) is True
    assert utils.compare_lists([1, 2], [3, 3]) is False


def test_current_streak():
    assert utils.current_streak([1, 2, 2, 1, 1, 1]) == [1, 3]


def test_longest_streak():
    assert utils.longest_streak([1, 2, 2, 2, 2, 1]) == [2, 4]
