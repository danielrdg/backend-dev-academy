def test_get_models(client):
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)

    for model in data:
        assert isinstance(model, dict)
        assert "id" in model
        assert "name" in model
