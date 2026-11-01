
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.database import Base, get_db
from app.main import app


def setup_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
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
    return TestClient(app), engine


def create_product_and_batch(client, quantity=10):
    client.post(
        "/produtos",
        data={
            "name": "Leite Integral",
            "category": "Laticínios",
            "unit": "unidade",
        },
    )

    response = client.post(
        "/lotes",
        data={
            "product_id": "1",
            "code": "LEITE001",
            "quantity": str(quantity),
            "received_at": "2026-11-01",
            "expires_at": "2026-11-15",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303


def run_test(test_action):
    client, engine = setup_test_client()
    try:
        return test_action(client)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_batch_successfully():
    def action(client):
        create_product_and_batch(client)
        response = client.get("/movimentacoes")
        assert response.status_code == 200
        assert "LEITE001" in response.text

    run_test(action)


def test_register_valid_stock_entry():
    def action(client):
        create_product_and_batch(client)
        response = client.post(
            "/movimentacoes",
            data={
                "batch_id": "1",
                "movement_type": "entrada",
                "quantity": "5",
                "notes": "Entrada de teste",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        page = client.get("/movimentacoes")
        assert "entrada" in page.text

    run_test(action)


def test_register_valid_stock_exit():
    def action(client):
        create_product_and_batch(client)
        response = client.post(
            "/movimentacoes",
            data={
                "batch_id": "1",
                "movement_type": "saida",
                "quantity": "3",
                "notes": "Saída de teste",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        page = client.get("/movimentacoes")
        assert "saida" in page.text

    run_test(action)


def test_block_stock_exit_above_available_quantity():
    def action(client):
        create_product_and_batch(client, quantity=5)
        response = client.post(
            "/movimentacoes",
            data={
                "batch_id": "1",
                "movement_type": "saida",
                "quantity": "6",
                "notes": "Saldo insuficiente",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/movimentacoes?erro=saldo"

    run_test(action)


def test_block_zero_quantity_movement():
    def action(client):
        create_product_and_batch(client)
        response = client.post(
            "/movimentacoes",
            data={
                "batch_id": "1",
                "movement_type": "entrada",
                "quantity": "0",
                "notes": "Quantidade zero",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/movimentacoes?erro=dados"

    run_test(action)
