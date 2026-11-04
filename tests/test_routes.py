def test_index_returns_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Flask Basics" in response.text


def test_static_route_registered(app):
    rules = {rule.endpoint for rule in app.url_map.iter_rules()}
    assert "static" in rules


def test_missing_resume_returns_404(app, client):
    app.config["LOGIN_DISABLED"] = True

    response = client.get("/resume/999")

    assert response.status_code == 404
    assert "Resume not found" in response.text


def test_about_page_renders_through_page_template(client):
    response = client.get("/about")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    # index.html wraps content in base.html, which includes nav/footer
    assert "<nav" in body
    assert "<footer" in body
    assert "<h1" in body and "About" in body
