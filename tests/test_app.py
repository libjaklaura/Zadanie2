from app import create_app
from app import routes


def test_homepage_is_numbered():
    client = create_app({"TESTING": True}).test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Authentication Bypass" in response.data
    assert b"Data Manipulation" in response.data


def test_routes_exist_without_database_connection():
    app = create_app({"TESTING": True})
    paths = {rule.rule for rule in app.url_map.iter_rules()}
    assert {"/auth", "/catalog", "/library", "/tracking", "/product"}.issubset(paths)


def test_tracking_vulnerable_field_executes_boolean_payload(monkeypatch):
    calls = []

    def fake_query(sql, params=None):
        calls.append((sql, params))
        return [{"?column?": 1}]

    monkeypatch.setattr(routes, "query", fake_query)
    client = create_app({"TESTING": True}).test_client()
    payload = "' OR 1=1 --"
    response = client.get("/tracking", query_string={"mode": "vulnerable", "tracking_number": payload})
    assert response.status_code == 200
    assert calls[0][1] is None
    assert payload in calls[0][0]
    assert b"Shipment found" in response.data


def test_tracking_vulnerable_field_supports_substring_inference(monkeypatch):
    calls = []

    def fake_query(sql, params=None):
        calls.append((sql, params))
        return []

    monkeypatch.setattr(routes, "query", fake_query)
    client = create_app({"TESTING": True}).test_client()
    payload = "' OR (SUBSTRING((SELECT tracking_number FROM shipments ORDER BY id LIMIT 1), 1, 1) = 'P') --"
    response = client.get("/tracking", query_string={"mode": "vulnerable", "tracking_number": payload})
    assert response.status_code == 200
    assert "SUBSTRING" in calls[0][0]
    assert b"Shipment not found" in response.data


def test_tracking_secure_field_parameterizes_the_same_injection_input(monkeypatch):
    calls = []

    def fake_query(sql, params=None):
        calls.append((sql, params))
        return []

    monkeypatch.setattr(routes, "query", fake_query)
    client = create_app({"TESTING": True}).test_client()
    payload = "' OR 1=1 --"
    response = client.get("/tracking", query_string={"mode": "secure", "tracking_number": payload})
    assert response.status_code == 200
    assert "%s" in calls[0][0]
    assert calls[0][1] == (payload,)
    assert b"Shipment not found" in response.data


def test_login_displays_seeded_demo_account(monkeypatch):
    def fake_query(sql, params=None):
        return [{"username": "student", "password": "LibraryPass-42"}]

    monkeypatch.setattr(routes, "query", fake_query)
    response = create_app({"TESTING": True}).test_client().get("/auth")
    assert b"student" in response.data
    assert b"LibraryPass-42" in response.data


def test_legitimate_login_succeeds_in_both_modes(monkeypatch):
    def fake_query(sql, params=None):
        if params in (("student", "LibraryPass-42"),) or (
            params is None and "student" in sql and "LibraryPass-42" in sql
        ):
            return [{"username": "student", "role": "Student"}]
        return []

    monkeypatch.setattr(routes, "query", fake_query)
    client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
    for selected_mode in ("vulnerable", "secure"):
        response = client.post("/auth", data={
            "mode": selected_mode,
            "username": "student",
            "password": "LibraryPass-42",
        })
        assert response.status_code == 302


def test_incorrect_login_fails_in_both_modes(monkeypatch):
    monkeypatch.setattr(routes, "query", lambda sql, params=None: [])
    client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
    for selected_mode in ("vulnerable", "secure"):
        response = client.post("/auth", data={
            "mode": selected_mode,
            "username": "student",
            "password": "wrong-password",
        })
        assert response.status_code == 200
        assert b"Sign-in failed" in response.data


def test_catalog_renders_na_for_null_union_price(monkeypatch):
    monkeypatch.setattr(routes, "query", lambda sql, params=None: [{
        "name": "Fictional union row",
        "price": None,
        "description": "A row with no price.",
    }])
    response = create_app({"TESTING": True}).test_client().get(
        "/catalog", query_string={"mode": "vulnerable", "q": "demo"}
    )
    assert response.status_code == 200
    assert b">N/A</strong>" in response.data


def test_product_reset_restores_price_and_seeded_reviews_in_both_modes(monkeypatch):
    seeded = {
        "product_id": 1,
        "reviewer_name": "Demo visitor",
        "review_text": "A reliable fictional laptop for coursework.",
    }

    class FakeCursor:
        def __init__(self, db):
            self.db = db

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql, params=None):
            self.db.calls.append((sql, params))
            normalized = " ".join(sql.split())
            if normalized.startswith("UPDATE products"):
                self.db.price = params[0]
            elif normalized.startswith("DELETE FROM reviews"):
                self.db.reviews = [review for review in self.db.reviews if review == seeded]
            elif normalized.startswith("INSERT INTO reviews"):
                if seeded not in self.db.reviews:
                    self.db.reviews.append(seeded.copy())

    class FakeDB:
        def __init__(self):
            self.price = 12.50
            self.reviews = [seeded.copy(), {
                "product_id": 1,
                "reviewer_name": "Test visitor",
                "review_text": "'; UPDATE products SET price = 1; --",
            }]
            self.calls = []
            self.commits = 0
            self.rollbacks = 0

        def cursor(self):
            return FakeCursor(self)

        def commit(self):
            self.commits += 1

        def rollback(self):
            self.rollbacks += 1

    for selected_mode in ("vulnerable", "secure"):
        db = FakeDB()
        monkeypatch.setattr(routes, "get_db", lambda db=db: db)
        response = create_app({"TESTING": True}).test_client().get(
            "/product", query_string={"mode": selected_mode, "reset": "1"}
        )
        assert response.status_code == 302
        assert db.price == 899.00
        assert db.reviews == [seeded]
        assert db.commits == 1
        assert db.rollbacks == 0
        assert all(params is not None for _sql, params in db.calls)
