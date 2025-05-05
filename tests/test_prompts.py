import pytest

@pytest.fixture
def sample_prompt():
    return {
        "name": "Prompt de Teste",
        "template": "Olá, {usuario}!",
        "ia_model": "gpt-3.5-turbo",
        "variables": ["usuario"]
    }

def test_create_prompt(client, sample_prompt):
    response = client.post("/prompts", json=sample_prompt)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == sample_prompt["name"]
    assert data["template"] == sample_prompt["template"]
    assert data["ia_model"] == sample_prompt["ia_model"]
    assert data["variables"] == sample_prompt["variables"]

def test_list_prompts_contains_created(client, sample_prompt):
    # Cria um prompt novo
    client.post("/prompts", json=sample_prompt)
    response = client.get("/prompts")
    assert response.status_code == 200
    prompts = response.json()
    assert any(p["name"] == sample_prompt["name"] for p in prompts)

def test_get_prompt_by_id(client, sample_prompt):
    # Cria e busca por ID
    post = client.post("/prompts", json=sample_prompt).json()
    pid = post["id"]
    response = client.get(f"/prompts/{pid}")
    assert response.status_code == 200
    got = response.json()
    assert got["id"] == pid
    assert got["name"] == sample_prompt["name"]

def test_update_prompt(client, sample_prompt):
    post = client.post("/prompts", json=sample_prompt).json()
    pid = post["id"]
    updated = sample_prompt.copy()
    updated["name"] = "Nome Atualizado"
    response = client.put(f"/prompts/{pid}", json=updated)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nome Atualizado"

def test_delete_prompt(client, sample_prompt):
    post = client.post("/prompts", json=sample_prompt).json()
    pid = post["id"]
    #Delete deve retornar 204 No Content
    response = client.delete(f"/prompts/{pid}")
    assert response.status_code == 204
    #GET deve dar 404
    response = client.get(f"/prompts/{pid}")
    assert response.status_code == 404

def test_metrics_prompt_new(client, sample_prompt):
    post = client.post("/prompts", json=sample_prompt).json()
    pid = post["id"]
    response = client.get(f"/prompts/{pid}/metrics")
    assert response.status_code == 200
    m = response.json()
    # Métricas iniciais devem existir e normalmente serem zero
    assert "total_executions" in m
    assert "avg_latency_ms" in m
    assert "avg_cost" in m
    assert isinstance(m["total_executions"], int)
