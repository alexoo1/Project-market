import pytest

from app.models.category import Category


def _register(client, phone, display_name):
    resp = client.post(
        "/api/v1/auth/register",
        json={"first_name": "Test", "display_name": display_name, "phone": phone,
              "password": "SuperSecret123", "city": "Abidjan"},
    )
    return resp.json()["access_token"]


def _me_id(client, token):
    return client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]


@pytest.fixture()
def category(db_session):
    cat = Category(name="Sneakers", slug="sneakers-social-test")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


def _create_listing(client, token, category_id, price=45000):
    payload = {
        "title": "Yeezy P5", "description": "Baskets tres bon etat, semelles peu usees, boite incluse.",
        "category_id": str(category_id), "condition": "very_good", "price": price,
        "city": "Cocody", "images": [{"url": "https://example.com/yeezy.jpg"}],
    }
    resp = client.post("/api/v1/listings", json=payload, headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


def _complete_order(client, seller_token, buyer_token, listing_id):
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    order = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "hand_delivery"}, headers=buyer_headers,
    ).json()
    client.post(f"/api/v1/orders/{order['id']}/pay", headers=buyer_headers)
    client.post(f"/api/v1/orders/{order['id']}/ship", headers=seller_headers)
    client.post(f"/api/v1/orders/{order['id']}/confirm-receipt", headers=buyer_headers)
    return order["id"]


# --- Reviews -------------------------------------------------------------

def test_review_requires_completed_order(client, category):
    seller_token = _register(client, "+2250744444401", "seller_rev1")
    buyer_token = _register(client, "+2250744444402", "buyer_rev1")
    listing_id = _create_listing(client, seller_token, category.id)

    order = client.post(
        f"/api/v1/listings/{listing_id}/purchase",
        json={"delivery_method": "hand_delivery"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    ).json()

    resp = client.post(
        f"/api/v1/orders/{order['id']}/reviews", json={"rating": 5},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert resp.status_code == 422


def test_review_updates_average_rating_and_prevents_duplicates(client, category):
    seller_token = _register(client, "+2250744444403", "seller_rev2")
    buyer_token = _register(client, "+2250744444404", "buyer_rev2")
    seller_id = _me_id(client, seller_token)
    listing_id = _create_listing(client, seller_token, category.id)
    order_id = _complete_order(client, seller_token, buyer_token, listing_id)

    review = client.post(
        f"/api/v1/orders/{order_id}/reviews", json={"rating": 5, "comment": "Nickel"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert review.status_code == 201

    duplicate = client.post(
        f"/api/v1/orders/{order_id}/reviews", json={"rating": 3},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert duplicate.status_code == 409

    seller_profile = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {seller_token}"}
    ).json()
    assert seller_profile["average_rating"] == 5.0
    assert seller_profile["review_count"] == 1

    public_reviews = client.get(f"/api/v1/users/{seller_id}/reviews").json()
    assert len(public_reviews) == 1


# --- Follows -------------------------------------------------------------

def test_follow_unfollow_is_idempotent(client):
    user_a_token = _register(client, "+2250744444405", "user_a")
    user_b_token = _register(client, "+2250744444406", "user_b")
    user_b_id = _me_id(client, user_b_token)
    headers = {"Authorization": f"Bearer {user_a_token}"}

    r1 = client.put(f"/api/v1/users/{user_b_id}/follow", headers=headers)
    r2 = client.put(f"/api/v1/users/{user_b_id}/follow", headers=headers)
    assert r1.status_code == 204
    assert r2.status_code == 204

    status_resp = client.get(f"/api/v1/users/{user_b_id}/follow-status", headers=headers)
    assert status_resp.json() == {"following": True, "followers_count": 1}

    client.delete(f"/api/v1/users/{user_b_id}/follow", headers=headers)
    status_after = client.get(f"/api/v1/users/{user_b_id}/follow-status", headers=headers)
    assert status_after.json() == {"following": False, "followers_count": 0}


def test_cannot_follow_self(client):
    token = _register(client, "+2250744444407", "user_self")
    user_id = _me_id(client, token)
    resp = client.put(f"/api/v1/users/{user_id}/follow", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


# --- Boosts -------------------------------------------------------------

def test_boost_only_owner_and_valid_duration(client, category):
    seller_token = _register(client, "+2250744444408", "seller_boost1")
    other_token = _register(client, "+2250744444409", "other_boost1")
    listing_id = _create_listing(client, seller_token, category.id)

    forbidden = client.post(
        f"/api/v1/listings/{listing_id}/boosts", json={"duration_hours": 24},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden.status_code == 403

    invalid_duration = client.post(
        f"/api/v1/listings/{listing_id}/boosts", json={"duration_hours": 999},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert invalid_duration.status_code == 422

    valid = client.post(
        f"/api/v1/listings/{listing_id}/boosts", json={"duration_hours": 24},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert valid.status_code == 201


def test_boosted_listing_appears_first_in_feed(client, category):
    seller_token = _register(client, "+2250744444410", "seller_boost2")
    older_id = _create_listing(client, seller_token, category.id)
    newer_id = client.post(
        "/api/v1/listings",
        json={
            "title": "Article plus recent", "description": "Un autre article recent pour tester le tri.",
            "category_id": str(category.id), "condition": "good", "price": 5000,
            "city": "Cocody", "images": [{"url": "https://example.com/x.jpg"}],
        },
        headers={"Authorization": f"Bearer {seller_token}"},
    ).json()["id"]

    # On booste l'annonce la plus ancienne -> elle doit passer en tête du feed,
    # peu importe l'ordre relatif par nouveauté (non fiable ici: les deux
    # annonces sont créées dans la même transaction de test, donc peuvent
    # partager un même timestamp `now()` côté PostgreSQL).
    client.post(
        f"/api/v1/listings/{older_id}/boosts", json={"duration_hours": 24},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    feed_after = client.get("/api/v1/listings").json()
    assert feed_after["items"][0]["id"] == older_id
    assert newer_id in [i["id"] for i in feed_after["items"]]


# --- Notifications -------------------------------------------------------------

def test_notifications_triggered_by_offer_and_marked_read(client, category):
    seller_token = _register(client, "+2250744444411", "seller_notif1")
    buyer_token = _register(client, "+2250744444412", "buyer_notif1")
    listing_id = _create_listing(client, seller_token, category.id)

    client.post(
        f"/api/v1/listings/{listing_id}/offers", json={"amount": 9000},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )

    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    notifications = client.get("/api/v1/notifications", headers=seller_headers).json()
    assert any(n["type"] == "new_offer" for n in notifications)

    unread = client.get("/api/v1/notifications/unread-count", headers=seller_headers).json()
    assert unread["count"] >= 1

    client.post("/api/v1/notifications/read-all", headers=seller_headers)
    unread_after = client.get("/api/v1/notifications/unread-count", headers=seller_headers).json()
    assert unread_after["count"] == 0
