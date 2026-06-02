def test_overview(client):
    assert client.get('/').status_code == 200


def test_schedule(client):
    assert client.get('/schedule/').status_code == 200


def test_workouts(client):
    assert client.get('/workouts/').status_code == 200


def test_nutrition(client):
    assert client.get('/nutrition/').status_code == 200


def test_supplements(client):
    assert client.get('/supplements/').status_code == 200


def test_hair(client):
    assert client.get('/hair/').status_code == 200


def test_skin(client):
    assert client.get('/skin/').status_code == 200


def test_shopping(client):
    assert client.get('/shopping/').status_code == 200


def test_myths(client):
    assert client.get('/myths/').status_code == 200
