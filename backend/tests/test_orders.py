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
    cat = Category(name="Homme", slug="homme-order-test")
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


def test_full_purchase_flow_direct_buy(client, category):
    seller_token = _register(client, "+2250733333301", "seller_ord1")
    buyer_token = _register(client, "+2250733333302", "buyer_ord1")
    listing_id = _create_listing(client, seller_token, category.id, price=8000)

    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    # Achat direct au prix affiché
    order_resp = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "pickup_point", "payment_method": "mock"},
        headers=buyer_headers,
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    assert order["item_price"] == 8000
    assert order["platform_fee"] == 400  # 5% de 8000
    assert order["delivery_fee"] == 1000  # pickup_point
    assert order["total"] == 9400
    assert order["status"] == "pending_payment"
    order_id = order["id"]

    # L'annonce doit être réservée pendant la commande en attente
    listing_after_order = client.get(f"/api/v1/listings/{listing_id}").json()
    assert listing_after_order["status"] == "reserved"

    # Paiement
    pay_resp = client.post(f"/api/v1/orders/{order_id}/pay", headers=buyer_headers)
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "paid"
    assert pay_resp.json()["payment"]["status"] == "succeeded"

    # Expédition (vendeur uniquement)
    forbidden_ship = client.post(f"/api/v1/orders/{order_id}/ship", headers=buyer_headers)
    assert forbidden_ship.status_code == 403

    ship_resp = client.post(f"/api/v1/orders/{order_id}/ship", headers=seller_headers)
    assert ship_resp.status_code == 200
    assert ship_resp.json()["status"] == "shipped"
    assert ship_resp.json()["delivery"]["tracking_number"] is not None

    # Confirmation de réception (acheteur uniquement)
    forbidden_confirm = client.post(f"/api/v1/orders/{order_id}/confirm-receipt", headers=seller_headers)
    assert forbidden_confirm.status_code == 403

    confirm_resp = client.post(f"/api/v1/orders/{order_id}/confirm-receipt", headers=buyer_headers)
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "completed"

    listing_final = client.get(f"/api/v1/listings/{listing_id}").json()
    assert listing_final["status"] == "sold"


def test_purchase_from_accepted_offer_uses_offer_amount(client, category):
    seller_token = _register(client, "+2250733333303", "seller_ord2")
    buyer_token = _register(client, "+2250733333304", "buyer_ord2")
    listing_id = _create_listing(client, seller_token, category.id, price=8000)

    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    seller_headers = {"Authorization": f"Bearer {seller_token}"}

    offer = client.post(
        f"/api/v1/listings/{listing_id}/offers", json={"amount": 6500}, headers=buyer_headers
    ).json()
    client.patch(f"/api/v1/offers/{offer['id']}/accept", headers=seller_headers)

    order_resp = client.post(
        f"/api/v1/offers/{offer['id']}/purchase",
        json={"delivery_method": "hand_delivery", "payment_method": "mock"},
        headers=buyer_headers,
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    assert order["item_price"] == 6500  # montant de l'offre, pas le prix affiché
    assert order["platform_fee"] == 325  # 5% de 6500
    assert order["delivery_fee"] == 0  # remise en main propre
    assert order["total"] == 6825


def test_cannot_buy_own_listing(client, category):
    seller_token = _register(client, "+2250733333305", "seller_ord3")
    listing_id = _create_listing(client, seller_token, category.id)

    resp = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "hand_delivery"},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert resp.status_code == 422


def test_cancel_order_releases_listing(client, category):
    seller_token = _register(client, "+2250733333306", "seller_ord4")
    buyer_token = _register(client, "+2250733333307", "buyer_ord4")
    listing_id = _create_listing(client, seller_token, category.id)
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

    order = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "hand_delivery"},
        headers=buyer_headers,
    ).json()

    assert client.get(f"/api/v1/listings/{listing_id}").json()["status"] == "reserved"

    cancel_resp = client.post(f"/api/v1/orders/{order['id']}/cancel", headers=buyer_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    assert client.get(f"/api/v1/listings/{listing_id}").json()["status"] == "active"


def test_only_participants_can_view_order(client, category):
    seller_token = _register(client, "+2250733333308", "seller_ord5")
    buyer_token = _register(client, "+2250733333309", "buyer_ord5")
    third_token = _register(client, "+2250733333310", "third_ord5")
    listing_id = _create_listing(client, seller_token, category.id)

    order = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "hand_delivery"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    ).json()

    forbidden = client.get(
        f"/api/v1/orders/{order['id']}", headers={"Authorization": f"Bearer {third_token}"}
    )
    assert forbidden.status_code == 403
