from app.core.config import settings


def _register(client, phone="+2250700000099"):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test",
            "display_name": "uploader",
            "phone": phone,
            "password": "SuperSecret123",
            "city": "Abidjan",
        },
    )
    return resp.json()["access_token"]


def _png_bytes() -> bytes:
    # PNG 1x1 minimal valide.
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d494844520000000100000001080600000"
        "01f15c4890000000a49444154789c6300010000050001"
        "0d0a2db40000000049454e44ae426082"
    )


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/v1/uploads/images",
        files=[("files", ("photo.png", _png_bytes(), "image/png"))],
    )
    assert resp.status_code in (401, 403)


def test_upload_rejects_disallowed_content_type(client):
    token = _register(client)
    resp = client.post(
        "/api/v1/uploads/images",
        headers={"Authorization": f"Bearer {token}"},
        files=[("files", ("doc.txt", b"hello", "text/plain"))],
    )
    assert resp.status_code == 422


def test_upload_image_returns_public_url(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_LOCAL_PATH", str(tmp_path))
    token = _register(client)
    resp = client.post(
        "/api/v1/uploads/images",
        headers={"Authorization": f"Bearer {token}"},
        files=[("files", ("photo.png", _png_bytes(), "image/png"))],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["images"]) == 1
    url = data["images"][0]["url"]
    assert url.startswith(settings.STORAGE_PUBLIC_BASE_URL)
    saved_files = list(tmp_path.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].suffix == ".png"


def test_upload_multiple_images(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_LOCAL_PATH", str(tmp_path))
    token = _register(client)
    resp = client.post(
        "/api/v1/uploads/images",
        headers={"Authorization": f"Bearer {token}"},
        files=[
            ("files", ("a.png", _png_bytes(), "image/png")),
            ("files", ("b.png", _png_bytes(), "image/png")),
        ],
    )
    assert resp.status_code == 200
    assert len(resp.json()["images"]) == 2
    assert len(list(tmp_path.iterdir())) == 2
