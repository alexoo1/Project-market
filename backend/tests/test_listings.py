import pytest

from app.models.brand import Brand
from app.models.category import Category


def _register(client, phone, display_name="user"):
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
    cat = Category(name="Femme", slug="femme-test")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


def _listing_payload(category_id, **overrides):
    payload = {
        "title": "Veste en jean oversize",
        "description": "Belle veste en jean, tres bon etat general, portee peu souvent.",
        "category_id": str(category_id),
        "size": "M",
        "condition": "very_good",
        "price": 15000,
        "city": "Cocody",
        "images": [{"url": "https://example.com/img1.jpg"}],
    }
    payload.update(overrides)
    return payload


def test_create_listing_requires_auth(client, category):
    resp = client.post("/api/v1/listings", json=_listing_payload(category.id))
    assert resp.status_code in (401, 403)


def test_create_and_fetch_listing(client, category):
    token = _register(client, "+2250711111101", "seller1")
    resp = client.post(
        "/api/v1/listings",
        json=_listing_payload(category.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["price"] == 15000
    assert len(body["images"]) == 1

    detail = client.get(f"/api/v1/listings/{body['id']}")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Veste en jean oversize"


def test_feed_returns_active_listings(client, category):
    token = _register(client, "+2250711111102", "seller2")
    client.post(
        "/api/v1/listings",
        json=_listing_payload(category.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.get("/api/v1/listings")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_search_by_price_range(client, category):
    token = _register(client, "+2250711111103", "seller3")
    client.post(
        "/api/v1/listings",
        json=_listing_payload(category.id, price=15000),
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.get("/api/v1/listings?price_min=20000")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_only_owner_can_update_listing(client, category):
    seller_token = _register(client, "+2250711111104", "seller4")
    buyer_token = _register(client, "+2250711111105", "buyer4")

    create_resp = client.post(
        "/api/v1/listings",
        json=_listing_payload(category.id),
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    listing_id = create_resp.json()["id"]

    forbidden = client.patch(
        f"/api/v1/listings/{listing_id}",
        json={"price": 1},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert forbidden.status_code == 403

    allowed = client.patch(
        f"/api/v1/listings/{listing_id}",
        json={"price": 12000},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["price"] == 12000


def test_favorite_flow_is_idempotent(client, category):
    seller_token = _register(client, "+2250711111106", "seller5")
    buyer_token = _register(client, "+2250711111107", "buyer5")

    create_resp = client.post(
        "/api/v1/listings",
        json=_listing_payload(category.id),
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    listing_id = create_resp.json()["id"]

    headers = {"Authorization": f"Bearer {buyer_token}"}
    r1 = client.put(f"/api/v1/favorites/{listing_id}", headers=headers)
    r2 = client.put(f"/api/v1/favorites/{listing_id}", headers=headers)
    assert r1.status_code == 204
    assert r2.status_code == 204

    favorites = client.get("/api/v1/favorites", headers=headers)
    assert len(favorites.json()) == 1

    remove = client.delete(f"/api/v1/favorites/{listing_id}", headers=headers)
    assert remove.status_code == 204
    favorites_after = client.get("/api/v1/favorites", headers=headers)
    assert len(favorites_after.json()) == 0
