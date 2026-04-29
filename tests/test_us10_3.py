import urllib.parse
from unittest.mock import patch


def test_oauth_redirect_contains_required_params(client, app):
    resp = client.get('/login/oauth/google')
    assert resp.status_code == 302
    location = resp.headers['Location']
    assert 'accounts.google.com/o/oauth2/auth' in location
    parsed = urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
    assert parsed['client_id'] == ['test-google-client-id']
    assert parsed['response_type'] == ['code']
    assert 'openid' in parsed['scope'][0]
    assert 'email' in parsed['scope'][0]
    assert 'profile' in parsed['scope'][0]
    assert 'state' in parsed
    assert 'redirect_uri' in parsed


def test_oauth_state_stored_in_session(client):
    client.get('/login/oauth/google')
    with client.session_transaction() as sess:
        assert 'oauth_state' in sess


def test_oauth_callback_wrong_state_returns_400(client):
    with client.session_transaction() as sess:
        sess['oauth_state'] = 'correct-state'
    resp = client.get('/login/oauth/callback?state=wrong-state&code=somecode')
    assert resp.status_code == 400


def test_oauth_callback_no_state_returns_400(client):
    # no oauth_state in session at all
    resp = client.get('/login/oauth/callback?state=anything&code=somecode')
    assert resp.status_code == 400


_FAKE_PROFILE = {
    'sub': '999888777',
    'email': 'oauth@example.com',
    'given_name': 'OAuth',
    'family_name': 'User',
}


def test_oauth_callback_flow_with_mocked_exchange(client):
    with client.session_transaction() as sess:
        sess['oauth_state'] = 'valid-state'

    with patch(
        'controllers.auth_controller._exchange_code_for_profile',
        return_value=_FAKE_PROFILE,
    ):
        resp = client.get('/login/oauth/callback?state=valid-state&code=fakecode')

    assert resp.status_code == 200
    data = resp.get_json()
    assert data['sub'] == '999888777'
    assert data['email'] == 'oauth@example.com'
    assert data['given_name'] == 'OAuth'
    assert data['family_name'] == 'User'
