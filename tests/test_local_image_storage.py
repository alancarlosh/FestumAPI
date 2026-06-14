from io import BytesIO
from types import SimpleNamespace

from PIL import Image

from app.core.config import get_settings
from app.services.provider_storage_service import ProviderStorageService


def _png_bytes() -> bytes:
    image = Image.new("RGB", (32, 24), color=(120, 40, 200))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_local_storage_uploads_variants_and_deletes_them(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("IMAGE_STORAGE_BACKEND", "local")
    monkeypatch.setenv("LOCAL_STORAGE_PATH", str(tmp_path))
    monkeypatch.setenv("MEDIA_PUBLIC_PATH", "/media")
    monkeypatch.delenv("LOCAL_PUBLIC_BASE_URL", raising=False)
    get_settings.cache_clear()

    service = ProviderStorageService()
    file = SimpleNamespace(
        filename="logo.png",
        content_type="image/png",
        file=BytesIO(_png_bytes()),
    )

    storage_path, asset_url = service.upload_logo("provider-1", file)

    assert storage_path == "providers/provider-1/logo/logo.webp"
    assert asset_url == "/media/providers/provider-1/logo/logo.webp"
    assert (tmp_path / storage_path).is_file()
    assert (tmp_path / "providers/provider-1/logo/variants/logo_thumb.webp").is_file()
    assert (tmp_path / "providers/provider-1/logo/variants/logo_medium.webp").is_file()

    signed_asset = service.build_signed_asset(storage_path)

    assert signed_asset.url == "/media/providers/provider-1/logo/variants/logo_medium.webp"
    assert signed_asset.original is not None
    assert signed_asset.original.url == "/media/providers/provider-1/logo/logo.webp"

    assert service.extract_storage_key(asset_url) == storage_path

    service.delete_file(storage_path)

    assert not (tmp_path / storage_path).exists()
    assert not (tmp_path / "providers/provider-1/logo/variants/logo_thumb.webp").exists()
    assert not (tmp_path / "providers/provider-1/logo/variants/logo_medium.webp").exists()
    get_settings.cache_clear()
