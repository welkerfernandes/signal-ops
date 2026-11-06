import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(str(tmp_path / 'test.db'))) as client:
        client.headers['X-API-Key'] = 'local-alpha'
        yield client

def test_authentication(client):
    client.headers['X-API-Key'] = 'wrong'
    assert client.get('/evaluations').status_code == 401

def test_console_and_contract(client):
    assert client.get('/').status_code == 200
    assert 'OPERATIONS' not in client.get('/').text
    assert client.get('/openapi.json').status_code == 200
    assert client.get('/health').json() == {'status': 'ok'}

def command(**changes):
    return {'service':'checkout','baseline_ms':[100]*30,'candidate_ms':[180]*30,'idempotency_key':'one',**changes}

def test_regression_and_replay(client):
    result = client.post('/evaluations', json=command()).json()
    assert result['decision'] == 'rollback'
    assert result['ci95'][0] > 0.15
    assert client.post('/evaluations', json=command()).json() == result
    assert len(client.get('/evaluations').json()) == 1
    assert client.post('/evaluations', json=command(service='other')).status_code == 409

def test_tenant_isolation(client):
    client.post('/evaluations', json=command())
    client.headers['X-API-Key'] = 'local-beta'
    assert client.get('/evaluations').json() == []

def test_safe_and_insufficient_data(client):
    assert client.post('/evaluations', json=command(candidate_ms=[101]*30)).json()['decision'] == 'promote'
    assert client.post('/evaluations', json=command(idempotency_key='two',baseline_ms=[100])).json()['decision'] == 'insufficient_data'

@pytest.mark.parametrize('changes', [{'baseline_ms':[-1]*30},{'candidate_ms':[]},{'max_regression':2}])
def test_invalid_samples(client, changes):
    assert client.post('/evaluations', json=command(**changes)).status_code == 422

def test_reproducible_and_uncertain():
    from app.domain import assess
    baseline = [100]*30
    candidate = [50,180]*15
    result = assess(baseline, candidate)
    assert result == assess(baseline, candidate)
    assert result['decision'] == 'hold'
    assert assess([0]*30,[100]*30)['decision'] == 'insufficient_data'
