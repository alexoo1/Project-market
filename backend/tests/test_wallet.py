import pytest

from app.models.category import Category


def _register(client, phone, display_name):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test", "display_name": display_name, "phone": phone,
            "password": "SuperSecret123", "city": "Abidjan",
        },
    )
    return resp.json()["access_token"]


@pytest.fixture()
def category(db_session):
    cat = Category(name="Homme", slug="homme-wallet-test")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


def _create_listing(client, token, category_id, price=8000):
    payload = {
        "title": "Chemise wax homme",
        "description": "Chemise artisanale en wax, cousue main, tres bel imprime.",
        "category_id": str(category_id),
        "condition": "good",
        "price": price,
        "city": "Abobo",
        "images": [{"url": "https://example.com/chemise.jpg"}],
    }
    resp = client.post("/api/v1/listings", json=payload, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


def _complete_purchase(client, buyer_headers, seller_headers, listing_id):
    order = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "pickup_point", "payment_method": "wave"},
        headers=buyer_headers,
    ).json()
    order_id = order["id"]
    client.post(f"/api/v1/orders/{order_id}/pay", headers=buyer_headers)
    client.post(f"/api/v1/orders/{order_id}/ship", headers=seller_headers)
    client.post(f"/api/v1/orders/{order_id}/confirm-receipt", headers=buyer_headers)
    return order_id


def test_wallet_starts_empty(client):
    token = _register(client, "+2250744444401", "wallet_empty")
    resp = client.get("/api/v1/wallet", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"balance": 0, "transactions": []}


def test_confirm_receipt_credits_seller_wallet(client, category):
    seller_token = _register(client, "+2250744444402", "seller_wallet1")
    buyer_token = _register(client, "+2250744444403", "buyer_wallet1")
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    listing_id = _create_listing(client, seller_token, category.id, price=8000)

    order_id = _complete_purchase(client, buyer_headers, seller_headers, listing_id)

    wallet = client.get("/api/v1/wallet", headers=seller_headers).json()
    assert wallet["balance"] == 8000
    assert len(wallet["transactions"]) == 1
    tx = wallet["transactions"][0]
    assert tx["type"] == "sale_credit"
    assert tx["status"] == "completed"
    assert tx["amount"] == 8000
    assert tx["order_id"] == order_id

    # Le portefeuille de l'acheteur ne doit rien contenir.
    buyer_wallet = client.get("/api/v1/wallet", headers=buyer_headers).json()
    assert buyer_wallet["balance"] == 0


def test_withdrawal_debits_balance_and_records_transaction(client, category):
    seller_token = _register(client, "+2250744444404", "seller_wallet2")
    buyer_token = _register(client, "+2250744444405", "buyer_wallet2")
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    listing_id = _create_listing(client, seller_token, category.id, price=10000)
    _complete_purchase(client, buyer_headers, seller_headers, listing_id)

    resp = client.post(
        "/api/v1/wallet/withdrawals",
        json={"method": "wave", "destination": "+2250700000000", "amount": 6000},
        headers=seller_headers,
    )
    assert resp.status_code == 200
    tx = resp.json()
    assert tx["type"] == "withdrawal"
    assert tx["status"] == "completed"
    assert tx["amount"] == 6000
    assert tx["withdrawal_method"] == "wave"
    assert tx["withdrawal_destination"] == "+2250700000000"

    wallet = client.get("/api/v1/wallet", headers=seller_headers).json()
    assert wallet["balance"] == 4000
    assert len(wallet["transactions"]) == 2


def test_withdrawal_rejected_when_balance_insufficient(client):
    token = _register(client, "+2250744444406", "seller_wallet3")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/v1/wallet/withdrawals",
        json={"method": "orange_money", "destination": "+2250700000001", "amount": 1000},
        headers=headers,
    )
    assert resp.status_code == 422
    assert "insuffisant" in resp.json()["detail"].lower()
