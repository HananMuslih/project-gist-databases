import os
import json
import pytest
import responses

from gists_database.importer import import_gists_to_database

from .config import TESTING_GISTS_PATHS
from .fixtures import clean_gists_database as gists_database, mocked_requests
from requests import exceptions


def _test_gist_from_json(db_connection, gist_data):
    query = "SELECT github_id, html_url, git_pull_url, git_push_url, commits_url, forks_url, public, created_at, updated_at, comments, comments_url FROM gists WHERE github_id = :github_id"
    cursor = db_connection.execute(query, {'github_id': gist_data['id']})
    gist = cursor.fetchone()

    assert gist[0] == gist_data['id']
    assert gist[1] == gist_data['html_url']
    assert gist[2] == gist_data['git_pull_url']
    assert gist[3] == gist_data['git_push_url']

    assert gist[4] == gist_data['commits_url']
    assert gist[5] == gist_data['forks_url']
    assert gist[6] == gist_data['public']
    assert gist[7] == gist_data['created_at']
    assert gist[8] == gist_data['updated_at']
    assert gist[9] == gist_data['comments']
    assert gist[10] == gist_data['comments_url']


@responses.activate
def test_importer_imports_data_correctly(
    gists_database, mocked_requests):

    import_gists_to_database(gists_database, 'gvanrossum')

    query = 'SELECT COUNT(*) FROM gists;'
    cursor = gists_database.execute(query)
    count = cursor.fetchone()[0]
    assert count == 7
    for testing_gist_path in TESTING_GISTS_PATHS:
        with open(testing_gist_path, 'r') as fp:
            gist_data = json.load(fp)
            _test_gist_from_json(gists_database, gist_data)


@responses.activate
def test_import_with_non_existent_user_raises(
    gists_database, mocked_requests):

    with pytest.raises(exceptions.HTTPError):
        import_gists_to_database(gists_database, 'rmotr-doesnt-exist')
        
