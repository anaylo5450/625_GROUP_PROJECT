"""#60 — Hide answers before starting a study session."""


def _register_login(client, username='studyuser', email='study@test.com'):
    client.post('/register', data={
        'firstname': 'Test', 'lastname': 'User',
        'username': username, 'email': email,
        'password': 'pass123', 'confirm_password': 'pass123',
    })
    client.post('/login', data={'username': username, 'password': 'pass123'})


def _create_deck(client, title='Study Deck'):
    resp = client.post('/deck/create', data={
        'title': title, 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })
    return int(resp.headers['Location'].rstrip('/').split('/')[-1])


def _add_card(client, deck_id, front, back):
    client.post(f'/deck/{deck_id}/card/create', data={'front': front, 'back': back})


def test_study_page_returns_200_for_owner(client):
    _register_login(client)
    deck_id = _create_deck(client)
    _add_card(client, deck_id, 'Front Q', 'Hidden Answer')

    resp = client.get(f'/deck/{deck_id}/study')
    assert resp.status_code == 200


def test_back_text_not_in_visible_html_element(client):
    """Answer text must only appear in the JS card data, not in any HTML element."""
    _register_login(client, 'hideuser', 'hide@test.com')
    deck_id = _create_deck(client, title='Hide Test')
    back_text = 'SECRETANSWER_UNIQUE_9182'
    _add_card(client, deck_id, 'Question Side', back_text)

    resp = client.get(f'/deck/{deck_id}/study')
    assert resp.status_code == 200

    # back text IS present in the page (inside the JS const cards JSON)
    assert back_text.encode() in resp.data

    # back text is NOT rendered as the text content of any HTML element
    # (the #cardBack div is empty in server-rendered HTML; JS fills it at runtime)
    assert f'>{back_text}<'.encode() not in resp.data


def test_study_page_returns_200_for_shared_user(client, app):
    # register both users before logging in as either
    client.post('/register', data={'firstname': 'A', 'lastname': 'B', 'username': 'sowner',
                                   'email': 'sowner@test.com', 'password': 'pass123',
                                   'confirm_password': 'pass123'})
    client.post('/register', data={'firstname': 'C', 'lastname': 'D', 'username': 'sreader',
                                   'email': 'sreader@test.com', 'password': 'pass123',
                                   'confirm_password': 'pass123'})
    client.post('/login', data={'username': 'sowner', 'password': 'pass123'})
    deck_id = _create_deck(client, title='Shared Study')
    _add_card(client, deck_id, 'Q', 'A')
    client.post(f'/deck/{deck_id}/share', data={'username': 'sreader'})
    client.get('/logout')

    client.post('/login', data={'username': 'sreader', 'password': 'pass123'})
    resp = client.get(f'/deck/{deck_id}/study')
    assert resp.status_code == 200
