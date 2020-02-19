import os
import requests

from .exceptions import APIKeyMissingError

TMDB_TOKEN = os.environ.get('TMDB_TOKEN', None)

if TMDB_TOKEN is None:
    raise APIKeyMissingError(
        "All methods require an API key or a Auth Token. See "
        "https://developers.themoviedb.org/3/getting-started/introduction "
        "for how to retrieve an authentication token from "
        "The Movie Database"
    )
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TMDB_TOKEN}"})
base_url = 'https://api.themoviedb.org/3/'

