def test_execute_prompt_flow(client):
    # Primeiro cria um prompt
    prompt_payload = {
        "name": "Exec Teste",
        "template": "Teste {x}",
        "ia_model": "gpt-3.5-turbo",
        "variables": ["x"]
    }
    pid = client.post("/prompts", json=prompt_payload).json()["id"]

    # Em seguida dispara execução
    exec_payload = {
        "prompt_id": pid,
        "input": {"type": "text", "data": "Olá!"},
        "variables": {"x": "mundo"},
        "ia_model": "gpt-3.5-turbo"
    }
    response = client.post("/execute", json=exec_payload)
    assert response.status_code == 200
    result = response.json()
    # Deve retornar as chaves definidas em ExecutionOut
    assert "output" in result
    assert "latency_ms" in result
    assert "cost" in result
    assert isinstance(result["latency_ms"], int)
    assert isinstance(result["cost"], float)
