def test_questions_list_empty(client):
    response = client.get("/questions")
    assert response.status_code == 200
    assert response.json() == []


def test_questions_search_empty(client):
    response = client.get("/questions/search?q=xyz_not_found")
    assert response.status_code == 200
    assert response.json() == []


def test_question_not_found(client):
    response = client.get("/questions/999999")
    assert response.status_code == 404


def test_questions_search_returns_results(client, seeded_db):
    response = client.get("/questions/search?q=matter")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "What is matter?" in data[0]["question"]


def test_get_question_by_id(client, seeded_db):
    response = client.get("/questions/1")
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is matter?"


def test_search_returns_html_for_htmx(client, seeded_db):
    response = client.get(
        "/questions/search?q=matter",
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "What is matter?" in response.text


def test_create_question_missing_fields(client):
    response = client.post("/questions", json={})
    assert response.status_code == 422


def test_create_question(client, seeded_db):
    response = client.post("/questions", json={
        "question": "What is energy?",
        "user_id": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is energy?"
    assert "id" in data


def test_create_duplicate_question(client, seeded_db):
    response = client.post("/questions", json={
        "question": "What is matter?",
        "user_id": 1,
    })
    assert response.status_code == 409


def test_index_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Skillsera" in response.text


def test_about_page_renders(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert "About Skillsera" in response.text
