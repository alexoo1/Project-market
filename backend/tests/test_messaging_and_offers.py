import pytest

from app.models.category import Category


def _register(client, phone, display_name):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test",
            "display_name": display_name,
            "phone": phone,
            "password": "SuperSecret123",
            "city": "Abidjan",
        },
    )
    return resp.json()["access_token"]


@pytest.fixture()
def category(db_session):
    cat = Category(name="Femme", slug="femme-msg-test")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


def _create_listing(client, token, category_id, **overrides):
    payload = {
        "title": "Robe wax imprimee",
        "description": "Robe artisanale en wax, tres bon etat, jamais portee.",
        "category_id": str(category_id),
        "condition": "new_without_tag",
        "price": 12000,
        "city": "Yopougon",
        "images": [{"url": "https://example.com/robe.jpg"}],
    }
    payload.update(overrides)
    resp = client.post("/api/v1/listings", json=payload, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


# --- Messagerie -------------------------------------------------------------

def test_start_conversation_is_idempotent(client, category):
    seller_token = _register(client, "+2250722222201", "seller_msg1")
    buyer_token = _register(client, "+2250722222202", "buyer_msg1")
    listing_id = _create_listing(client, seller_token, category.id)

    headers = {"Authorization": f"Bearer {buyer_token}"}
    r1 = client.post("/api/v1/conversations", json={"listing_id": listing_id}, headers=headers)
    r2 = client.post("/api/v1/conversations", json={"listing_id": listing_id}, headers=headers)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]


def test_only_participants_can_read_messages(client, category):
    seller_token = _register(client, "+2250722222203", "seller_msg2")
    buyer_token = _register(client, "+2250722222204", "buyer_msg2")
    third_token = _register(client, "+2250722222205", "third_msg2")
    listing_id = _create_listing(client, seller_token, category.id)

    conv = client.post(
        "/api/v1/conversations", json={"listing_id": listing_id},
        headers={"Authorization": f"Bearer {buyer_token}"},
    ).json()

    forbidden = client.get(
        f"/api/v1/conversations/{conv['id']}/messages",
        headers={"Authorization": f"Bearer {third_token}"},
    )
    assert forbidden.status_code == 403


def test_message_flow_and_unread_count(client, category):
    seller_token = _register(client, "+2250722222206", "seller_msg3")
    buyer_token = _register(client, "+2250722222207", "buyer_msg3")
    listing_id = _create_listing(client, seller_token, category.id)

    conv = client.post(
        "/api/v1/conversations", json={"listing_id": listing_id},
        headers={"Authorization": f"Bearer {buyer_token}"},
    ).json()

    client.post(
        f"/api/v1/conversations/{conv['id']}/messages", json={"content": "Bonjour !"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )

    seller_conversations = client.get(
        "/api/v1/conversations", headers={"Authorization": f"Bearer {seller_token}"}
    ).json()
    assert seller_conversations[0]["unread_count"] == 1

    # Lire les messages marque comme lu
    client.get(
        f"/api/v1/conversations/{conv['id']}/messages",
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    seller_conversations_after = client.get(
        "/api/v1/conversations", headers={"Authorization": f"Bearer {seller_token}"}
    ).json()
    assert seller_conversations_after[0]["unread_count"] == 0


# --- Offres -------------------------------------------------------------

def test_cannot_offer_on_own_listing(client, category):
    seller_token = _register(client, "+2250722222208", "seller_off1")
    listing_id = _create_listing(client, seller_token, category.id)

    resp = client.post(
        f"/api/v1/listings/{listing_id}/offers", json={"amount": 9000},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert resp.status_code == 422


def test_duplicate_active_offer_is_rejected(client, category):
    seller_token = _register(client, "+2250722222209", "seller_off2")
    buyer_token = _register(client, "+2250722222210", "buyer_off2")
    listing_id = _create_listing(client, seller_token, category.id)

    headers = {"Authorization": f"Bearer {buyer_token}"}
    r1 = client.post(f"/api/v1/listings/{listing_id}/offers", json={"amount": 9000}, headers=headers)
    r2 = client.post(f"/api/v1/listings/{listing_id}/offers", json={"amount": 8000}, headers=headers)
    assert r1.status_code == 201
    assert r2.status_code == 409


def test_only_other_party_can_respond_to_offer(client, category):
    seller_token = _register(client, "+2250722222211", "seller_off3")
    buyer_token = _register(client, "+2250722222212", "buyer_off3")
    listing_id = _create_listing(client, seller_token, category.id)

    offer = client.post(
        f"/api/v1/listings/{listing_id}/offers", json={"amount": 9000},
        headers={"Authorization": f"Bearer {buyer_token}"},
    ).json()

    # L'acheteur ne peut pas accepter sa propre offre
    self_accept = client.patch(
        f"/api/v1/offers/{offer['id']}/accept", headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert self_accept.status_code == 403

    # Le vendeur peut accepter
    seller_accept = client.patch(
        f"/api/v1/offers/{offer['id']}/accept", headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert seller_accept.status_code == 200
    assert seller_accept.json()["status"] == "accepted"


def test_counter_offer_chain_and_listing_reservation(client, category):
    seller_token = _register(client, "+2250722222213", "seller_off4")
    buyer_token = _register(client, "+2250722222214", "buyer_off4")
    listing_id = _create_listing(client, seller_token, category.id)

    offer = client.post(
        f"/api/v1/listings/{listing_id}/offers", json={"amount": 9000},
        headers={"Authorization": f"Bearer {buyer_token}"},
    ).json()

    counter = client.post(
        f"/api/v1/offers/{offer['id']}/counter", json={"amount": 10500},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert counter.status_code == 201
    counter_body = counter.json()
    assert counter_body["proposed_by"] == "seller"
    assert counter_body["parent_offer_id"] == offer["id"]

    # Le vendeur ne peut pas accepter sa propre contre-offre
    self_accept = client.patch(
        f"/api/v1/offers/{counter_body['id']}/accept",
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert self_accept.status_code == 403

    # L'acheteur accepte -> l'annonce passe en reserved
    buyer_accept = client.patch(
        f"/api/v1/offers/{counter_body['id']}/accept",
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert buyer_accept.status_code == 200

    listing = client.get(f"/api/v1/listings/{listing_id}").json()
    assert listing["status"] == "reserved"
