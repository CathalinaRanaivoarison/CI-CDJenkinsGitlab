import pytest

from main import app


@pytest.fixture
def client():
    """Créer un client de test Flask."""
    app.config["TESTING"] = True
    # En mode TESTING, Flask relance les exceptions au lieu d'appeler le handler 500.
    # On le désactive pour pouvoir tester le gestionnaire d'erreurs.
    app.config["PROPAGATE_EXCEPTIONS"] = False
    with app.test_client() as client:
        yield client


def test_hello(client):
    """Test de la route principale."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"Hello World"


def test_health(client):
    """Test du health check utilisé par le pipeline."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_500_error(client):
    """Le handler 500 renvoie un message générique sans fuite d'information."""
    response = client.get("/error")
    assert response.status_code == 500
    assert b"An internal error occurred" in response.data
    assert b"Test Error" not in response.data
