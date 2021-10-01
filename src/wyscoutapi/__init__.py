import base64
import json

import requests
import ratelimiter


# Exceptions

class WyscoutAPIError(Exception):
    pass


class AuthenticationError(WyscoutAPIError):
    pass


class BadRequestError(WyscoutAPIError):
    pass


class TooManyRequestsError(WyscoutAPIError):
    pass


class UnknownError(WyscoutAPIError):
    pass


# Loaders

class WyscoutAPILoader:
    BASE_URL = 'https://apirest.wyscout.com'

    def __init__(self, username, password, version='v3', requests_per_sec=12):
        # Saving username and password as attributes is not necessary
        # It may occassionally be useful to view the username,
        # But we don't want password to be viewable as a plaintext attribute to minimise
        # the risk of it accidentally leaking a user's password
        # (even if it can be viewed in the header...)
        self.username = username

        self.version = version
        self.rate_limiter = ratelimiter.RateLimiter(max_calls=requests_per_sec, period=1)

        auth = base64.b64encode(f'{username}:{password}'.encode())
        self.headers = {'Authorization': 'Basic {auth}'.format(auth=auth.decode())}

    def _url(self, *route, **params):
        return '{base}/{version}/{route}'.format(
            base=self.BASE_URL,
            version=self.version,
            route='/'.join(str(r) for r in route)
        )

    def _parse_response(self, response):
        content = response.json()
        try:
            error = content.get('error', None)
        except AttributeError:
            # API call returned a list
            return content

        if error:
            if isinstance(error, str):
                raise UnknownError(error)
            if error['code'] == 401:
                raise AuthenticationError(error['message'])
            elif error['code'] == 400:
                raise BadRequestError(error['message'])
            elif error['code'] == 429:
                raise TooManyRequestsError(error['message'])
            else:
                raise UnknownError(error['message'])

        return content

    def get_route_json(self, *route, **params):
        for param, val in params.items():
            if isinstance(param, bool):
                params[param] = json.dumps(val)  # So that True -> 'true'

        with self.rate_limiter:
            r = requests.get(self._url(*route), headers=self.headers, params=params)

        return self._parse_response(r)


# API Client

class APIClient:
    """
    A wrapper for the Wyscout football data API v2 & v3
    """

    def __init__(self, loader):
        self.loader = loader

    # Areas

    def areas(self, details=None, fetch=None):
        return self.loader.get_route_json('areas', details=details, fetch=fetch)

    # Coaches

    def coach(self, coach_id, details=None, fetch=None):
        """ Retrieves information about a given coach. """
        return self.loader.get_route_json('coaches', coach_id, details=details, fetch=fetch)

    # Competitions

    def competitions(self, area_id, details=None, fetch=None):
        """ Returns a list of competitions for a given area. """
        return self.loader.get_route_json('competitions', areaId=area_id, details=details, fetch=fetch)

    def competition(self, competition_id, details=None, fetch=None):
        """ Retrieves information about a given competition. """
        return self.loader.get_route_json('competitions', competition_id, details=details, fetch=fetch)

    def competition_seasons(self, competition_id, active=False, details=None, fetch=None):
        """ Returns the list of seasons of the given competition. """
        return self.loader.get_route_json('competitions', competition_id, 'seasons', active=active, details=details, fetch=fetch)

    def competition_matches(self, competition_id, details=None, fetch=None):
        """ Returns the list of matches of the given competition in the current season. """
        return self.loader.get_route_json('competitions', competition_id, 'matches', details=details, fetch=fetch)

    def competition_players(self, competition_id, details=None, fetch=None):
        """ Returns the list of players of the given competition in the current season. """
        return self.loader.get_route_json('competitions', competition_id, 'players', details=details, fetch=fetch)

    def competition_teams(self, competition_id, details=None, fetch=None):
        """ Returns the list of teams of the given competition in the current season. """
        return self.loader.get_route_json('competitions', competition_id, 'teams', details=details, fetch=fetch)

    # Matches

    def match(self, match_id, use_sides=False, details=None, fetch=None):
        """ Retrieves information about a given match. """
        return self.loader.get_route_json('matches', match_id, useSides=use_sides, details=details, fetch=fetch)

    # Players

    def player(self, player_id, image_data_url=False, details=None, fetch=None):
        """ Retrieves information about a given player. """
        return self.loader.get_route_json('players', player_id, imageDataURL=image_data_url, details=details, fetch=fetch)

    def player_career(self, player_id, details=None, fetch=None):
        """ Retrieves aggregated career information about a given player. """
        return self.loader.get_route_json('players', player_id, 'career', details=details, fetch=fetch)

    def player_transfer(self, player_id, details=None, fetch=None):
        """ Retrieves a given player's transfers. """
        return self.loader.get_route_json('players', player_id, 'transfer', details=details, fetch=fetch)

    def player_matches(self, player_id, details=None, fetch=None):
        """ Returns the list of matches played by the given player in the current season. """
        return self.loader.get_route_json('players', player_id, 'matches', details=details, fetch=fetch)

    def player_fixtures(self, player_id, details=None, fetch=None):
        """ Retrieves all the fixtures matches for the given player. """
        return self.loader.get_route_json('players', player_id, 'fixtures', details=details, fetch=fetch)

    # Referees

    def referee(self, referee_id, details=None, fetch=None):
        """ Retrieves informations about a given referee. """
        return self.loader.get_route_json('referees', referee_id, details=details, fetch=fetch)

    # Rounds

    def round(self, round_id, details=None, fetch=None):
        """ Retrieves information about a given round. """
        return self.loader.get_route_json('rounds', round_id, details=details, fetch=fetch)

    # Search

    def search(self, query, object_type, details=None, fetch=None):
        """
        Returns a list of objects, matching the provided search string.

        For example:
        >>> w = WyscoutAPI()
        >>> w.search('totti', 'player')
        """
        return self.loader.get_route_json('search', query=query, objType=object_type, details=details, fetch=fetch)

    # Seasons

    def season(self, season_id, details=None, fetch=None):
        """ Retrieves information about a given season. """
        return self.loader.get_route_json('seasons', season_id, details=details, fetch=fetch)

    def season_career(self, season_id, filters=None, details=None, fetch=None):
        """ Retrieves all the team's information for the given season. """
        return self.loader.get_route_json('seasons', season_id, 'career', filters=filters or {}, details=details, fetch=fetch)

    def season_matches(self, season_id, details=None, fetch=None):
        """ Returns the list of matches played in the given season. """
        return self.loader.get_route_json('seasons', season_id, 'matches', details=details, fetch=fetch)

    def season_fixtures(self, season_id, details=None, fetch=None):
        """ Retrieves all the matches for the given season. """
        return self.loader.get_route_json('seasons', season_id, 'fixtures', details=details, fetch=fetch)

    def season_players(self, season_id, details=None, fetch=None):
        """ Returns the list of players in the given season. """
        return self.loader.get_route_json('seasons', season_id, 'players', details=details, fetch=fetch)

    def season_teams(self, season_id, details=None, fetch=None):
        """ Returns the list of teams in the given season. """
        return self.loader.get_route_json('seasons', season_id, 'teams', details=details, fetch=fetch)

    def season_standings(self, season_id, details=None, fetch=None):
        """ Retrieves all the standing's information for the given season. """
        return self.loader.get_route_json('seasons', season_id, 'standings', details=details, fetch=fetch)

    # Teams

    def team(self, team_id, image_data_url=False, details=None, fetch=None):
        """ Retrieves informations about a given team. """
        return self.loader.get_route_json('teams', team_id, imageDataURL=image_data_url, details=details, fetch=fetch)

    def team_matches(self, team_id, details=None, fetch=None):
        """ Returns the list of matches played by the given team. """
        return self.loader.get_route_json('teams', team_id, 'matches', details=details, fetch=fetch)

    def team_fixtures(self, team_id, details=None, fetch=None):
        """ Retrieves all the fixtures matches for the given team. """
        return self.loader.get_route_json('teams', team_id, 'fixtures', details=details, fetch=fetch)

    def team_squad(self, team_id, season_id=None, details=None, fetch=None):
        """ Returns the list of players currently playing for the given team. """
        return self.loader.get_route_json('teams', team_id, 'squad', seasonId=season_id, details=details, fetch=fetch)

    def team_career(self, team_id, season_id=None, details=None, fetch=None):
        """ Retrieves all the team's information for the given season. """
        return self.loader.get_route_json('teams', team_id, 'career', details=details, fetch=fetch)

    # Statistics Pack

    def player_advancedstats(self, player_id, competition_id, season_id=None,
                             round_id=None, match_day=None):
        """
        Returns advanced statistics of a given player in a specific competition's
        season. The statistics provided are relative globally to the selected season,
        not to a specific team.
        """
        return self.loader.get_route_json('players', player_id, 'advancedstats',
                                          compId=competition_id,
                                          seasonId=season_id,
                                          roundId=round_id,
                                          matchDay=match_day)

    def team_advancedstats(self, team_id, competition_id, season_id=None,
                             round_id=None, match_day=None):
        """
        Returns advanced statistics of a given team in a specific competition's
        season. The statistics provided are relative globally to the selected season.
        """
        return self.loader.get_route_json('teams', team_id, 'advancedstats',
                                          compId=competition_id,
                                          seasonId=season_id,
                                          roundId=round_id,
                                          matchDay=match_day)

    # Events pack

    def match_events(self, match_id, details=None, fetch=None):
        """ Retrieves informations about a given match's events. """
        return self.loader.get_route_json('matches', match_id, 'events', details=details, fetch=fetch)

    # Injuries pack

    def player_injuries(self, player_id):
        """ BETA: Returns the list of injuries for a given player. """
        return self.loader.get_route_json('players', player_id, 'injuries')

    # Extra

    def updated_objects(self, timestamp, object_type):
        """
        Specific API call to keep track of updates to the Wyscout database
        objects on a daily basis.
        Where [timestamp] is in the format YYYY-MM-DD HH:MM:SS (example: 2018-02-09 18:00:00),
        you can go back for a max of 168 hours (1 week) of the current time
        and [object_type] can be one of the following:
            areas, coaches, competitions, matches, playercareers, players,
            referees, rounds, seasons, teamcareers, teams, transfers
        """
        return self.loader.get_route_json('updatedobjects', updated_since=timestamp, type=object_type)[object_type]


class WyscoutAPI(APIClient):
    """
    Wyscout API Client using the live Wyscout Data API (see https://apidocs.wyscout.com/)
    """

    def __init__(self, username, password, version='v3', requests_per_sec=12):
        self.loader = WyscoutAPILoader(
            username=username,
            password=password,
            version=version,
            requests_per_sec=requests_per_sec
        )
