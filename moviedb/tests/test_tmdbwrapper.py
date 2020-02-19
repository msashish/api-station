from pytest import fixture
from moviedb.tmdbwrapper.tv import TV
import vcr


@fixture
def tv_keys():
    # Responsible only for returning the test data
    return ['id', 'origin_country', 'poster_path', 'name',
            'overview', 'popularity', 'backdrop_path',
            'first_air_date', 'vote_count', 'vote_average']


@vcr.use_cassette('tests/vcr_cassettes/tv-info.yml')
def test_tv_info(tv_keys):
    tv = TV(1396)
    response = tv.info()
    assert isinstance(response, dict)
    assert response['id'] == 1396
    assert set(tv_keys).issubset(response.keys())


@vcr.use_cassette('tests/vcr_cassettes/tv-top-rated.yml')
def test_tv_top_rated(tv_keys):
    response = TV.top_rated()
    assert isinstance(response, dict)
    assert isinstance(response['results'], list)
    assert set(tv_keys).issubset(response['results'][0].keys())

