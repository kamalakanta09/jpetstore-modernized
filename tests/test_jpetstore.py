from fastapi.testclient import TestClient
from app.main import app


def test_full_jpetstore_modernization_lifecycle():
    with TestClient(app) as client:
        # 1. Verify Catalog & Seed Parity
        cats = client.get("/api/v1/categories").json()
        assert len(cats) == 5
        assert any(c["catid"] == "FISH" for c in cats)

        # 2. Verify Case-Insensitive Product Search Parity
        search = client.get("/api/v1/products/search?q=shark").json()
        assert len(search) == 1
        assert search[0]["productid"] == "FI-SW-02"

        # 3. Verify Legacy Account Authentication (j2ee / j2ee)
        auth = client.post("/api/v1/auth/token", data={"username": "j2ee", "password": "j2ee"})
        assert auth.status_code == 200
        token = auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Verify Transactional Order Placement & Inventory Decrement
        initial_stock = client.get("/api/v1/items/EST-1").json()["quantity_available"]
        order_res = client.post(
            "/api/v1/orders",
            json={"items": [{"itemid": "EST-1", "quantity": 3}]},
            headers=headers,
        )
        assert order_res.status_code == 201
        order_data = order_res.json()
        assert float(order_data["totalprice"]) == 49.50  # 3 * 16.50
        assert order_data["orderid"] >= 1000

        updated_stock = client.get("/api/v1/items/EST-1").json()["quantity_available"]
        assert updated_stock == initial_stock - 3

        # 5. Verify ACID Rollback Guard on Insufficient Inventory
        fail_res = client.post(
            "/api/v1/orders",
            json={"items": [
                {"itemid": "EST-1", "quantity": 2},
                {"itemid": "EST-2", "quantity": 999999},  # Exceeds 10,000 stock
            ]},
            headers=headers,
        )
        assert fail_res.status_code == 409
        # EST-1 stock MUST NOT have decreased by 2 because the transaction rolled back
        after_rollback_stock = client.get("/api/v1/items/EST-1").json()["quantity_available"]
        assert after_rollback_stock == updated_stock
    