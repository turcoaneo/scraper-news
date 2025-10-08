import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_cluster_route(client):
    response = client.get("/cluster")
    assert response.status_code == 200

    clusters = response.get_json()
    assert isinstance(clusters, list)

    for cluster in clusters:
        assert "keywords" in cluster
        assert "titles" in cluster
        assert "urls" in cluster
        assert isinstance(cluster["keywords"], list)
        assert isinstance(cluster["titles"], list)
        assert isinstance(cluster["urls"], list)
