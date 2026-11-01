
import pytest
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # Cria um banco SQLite temporário, isolado do banco real.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_create_product_successfully(client):
    response = client.post(
        "/produtos",
        data={
            "name": "Arroz Integral",
            "category": "Mercearia",
            "unit": "pacote",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/produtos"

    page = client.get("/produtos")

    assert page.status_code == 200
    assert "Arroz Integral" in page.text
    assert "Mercearia" in page.text


def test_create_product_with_empty_name(client):
    response = client.post(
        "/produtos",
        data={
            "name": "   ",
            "category": "Mercearia",
            "unit": "pacote",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/produtos?erro=campos"


def test_prevent_duplicate_product(client):
    product_data = {
        "name": "Feijão",
        "category": "Mercearia",
        "unit": "pacote",
    }

    first_response = client.post(
        "/produtos",
        data=product_data,
        follow_redirects=False,
    )

    second_response = client.post(
        "/produtos",
        data=product_data,
        follow_redirects=False,
    )

    assert first_response.status_code == 303
    assert second_response.status_code == 303
    assert second_response.headers["location"] == "/produtos?erro=duplicado"
