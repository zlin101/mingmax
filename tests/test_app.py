from app.main import app


def test_app_creates_successfully() -> None:
    assert app is not None
    assert app.title == "mingmax"
    assert app.version == "0.1.0"


def test_app_has_v1_routes() -> None:
    routes = [route.path for route in app.routes]
    assert "/api/v1/health" in routes
