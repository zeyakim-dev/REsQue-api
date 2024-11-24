import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_endpoint(client):
    # When
    response = client.get('/')
    
    # Then
    assert response.status_code == 200
    assert response.json == {'message': 'Hello, DDD!'}