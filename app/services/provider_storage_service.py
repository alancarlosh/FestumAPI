from io import BytesIO
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.core.exceptions import ApiError, ServiceUnavailableError
from app.schemas.asset import SignedAssetResponse, SignedAssetVariantResponse

if TYPE_CHECKING:
    from fastapi import UploadFile


class ProviderStorageService:
    allowed_content_types = {"image/webp", "image/png", "image/jpeg"}
    max_file_size_bytes = 10 * 1024 * 1024  # 10 MB

    def __init__(self) -> None:
        self._s3_client_cached = None

    def upload_logo(self, provider_id: str, file: "UploadFile") -> tuple[str, str]:
        storage_path = f"providers/{provider_id}/logo/logo.webp"
        return self._upload_file(file=file, storage_path=storage_path)

    def upload_photo(self, provider_id: str, file: "UploadFile") -> tuple[str, str]:
        file_id = uuid4().hex
        storage_path = f"providers/{provider_id}/photos/{file_id}.webp"
        return self._upload_file(file=file, storage_path=storage_path)

    def upload_service_image(
        self,
        provider_id: str,
        service_id: str,
        file: "UploadFile",
    ) -> tuple[str, str]:
        file_id = uuid4().hex
        storage_path = f"providers/{provider_id}/services/{service_id}/images/{file_id}.webp"
        return self._upload_file(file=file, storage_path=storage_path)

    def upload_product_image(
        self,
        provider_id: str,
        service_id: str,
        product_id: str,
        file: "UploadFile",
    ) -> tuple[str, str]:
        file_id = uuid4().hex
        storage_path = (
            f"providers/{provider_id}/services/{service_id}/products/{product_id}/images/{file_id}.webp"
        )
        return self._upload_file(file=file, storage_path=storage_path)

    def _upload_file(self, file: "UploadFile", storage_path: str) -> tuple[str, str]:
        self._validate_file(file)

        content = file.file.read()
        if not content:
            raise ApiError("Image file is empty")
        if len(content) > self.max_file_size_bytes:
            raise ApiError("Image file exceeds the 10 MB limit")

        normalized_storage_path = storage_path.replace("\\", "/")
        variants = self._build_webp_variants(content)
        variant_keys = self._build_variant_keys(normalized_storage_path)
        self._upload_content(normalized_storage_path, variants["original"])
        self._upload_content(variant_keys["thumb"], variants["thumb"])
        self._upload_content(variant_keys["medium"], variants["medium"])
        asset_url = self._build_asset_url(normalized_storage_path)
        return normalized_storage_path, asset_url

    def delete_file(self, storage_path: str) -> None:
        if not storage_path:
            return
        normalized_storage_path = storage_path.replace("\\", "/").lstrip("/")
        variant_keys = self._build_variant_keys(normalized_storage_path)
        self._delete_content(normalized_storage_path)
        self._delete_content(variant_keys["thumb"])
        self._delete_content(variant_keys["medium"])

    def build_signed_asset(
        self,
        storage_path: str,
        ttl_seconds: int | None = None,
    ) -> SignedAssetResponse:
        normalized_storage_path = self.extract_storage_key(storage_path)
        if not normalized_storage_path:
            raise ApiError("Image key is required to generate a signed URL")

        settings = get_settings()
        if settings.image_storage_backend == "local":
            original_asset = self._build_local_asset_for_key(
                key=normalized_storage_path,
                ttl_seconds=ttl_seconds,
            )
            variant_keys = self._build_variant_keys(normalized_storage_path)
            thumb_asset = self._build_local_variant_or_original_asset(
                variant_key=variant_keys["thumb"],
                original_asset=original_asset,
                ttl_seconds=ttl_seconds,
            )
            medium_asset = self._build_local_variant_or_original_asset(
                variant_key=variant_keys["medium"],
                original_asset=original_asset,
                ttl_seconds=ttl_seconds,
            )
            return SignedAssetResponse(
                key=medium_asset.key,
                url=medium_asset.url,
                expires_at=medium_asset.expires_at,
                thumb=thumb_asset,
                medium=medium_asset,
                original=original_asset,
            )

        bucket_name = settings.s3_bucket_name
        if not bucket_name:
            raise ServiceUnavailableError("S3 bucket is not configured. Verify S3_BUCKET_NAME.")

        expires_in = ttl_seconds or settings.s3_presigned_ttl_seconds
        expires_in = max(60, min(expires_in, 3600))

        BotoCoreError, ClientError = self._get_s3_error_classes()
        try:
            s3_client = self._get_s3_client()
            original_asset = self._build_signed_asset_for_key(
                s3_client=s3_client,
                bucket_name=bucket_name,
                key=normalized_storage_path,
                expires_in=expires_in,
            )
            variant_keys = self._build_variant_keys(normalized_storage_path)
            thumb_asset = self._build_variant_or_original_asset(
                s3_client=s3_client,
                bucket_name=bucket_name,
                variant_key=variant_keys["thumb"],
                original_asset=original_asset,
                expires_in=expires_in,
            )
            medium_asset = self._build_variant_or_original_asset(
                s3_client=s3_client,
                bucket_name=bucket_name,
                variant_key=variant_keys["medium"],
                original_asset=original_asset,
                expires_in=expires_in,
            )

            return SignedAssetResponse(
                key=medium_asset.key,
                url=medium_asset.url,
                expires_at=medium_asset.expires_at,
                thumb=thumb_asset,
                medium=medium_asset,
                original=original_asset,
            )
        except (BotoCoreError, ClientError) as exc:
            raise ServiceUnavailableError(
                "Failed to generate signed URL for S3 image."
            ) from exc

    def build_signed_asset_lite(
        self,
        storage_path: str,
        *,
        ttl_seconds: int | None = None,
        preferred_variant: str = "thumb",
    ) -> SignedAssetResponse:
        normalized_storage_path = self.extract_storage_key(storage_path)
        if not normalized_storage_path:
            raise ApiError("Image key is required to generate a signed URL")

        settings = get_settings()
        if settings.image_storage_backend == "local":
            preferred = preferred_variant if preferred_variant in {"thumb", "medium"} else "thumb"
            variant_keys = self._build_variant_keys(normalized_storage_path)
            selected_key = variant_keys["thumb"] if preferred == "thumb" else variant_keys["medium"]
            if not self._local_object_exists(selected_key):
                selected_key = normalized_storage_path
            selected_asset = self._build_local_asset_for_key(
                key=selected_key,
                ttl_seconds=ttl_seconds,
            )
            thumb_asset = selected_asset if selected_key == variant_keys["thumb"] else None
            medium_asset = selected_asset if selected_key == variant_keys["medium"] else None
            original_asset = selected_asset if selected_key == normalized_storage_path else None
            return SignedAssetResponse(
                key=selected_asset.key,
                url=selected_asset.url,
                expires_at=selected_asset.expires_at,
                thumb=thumb_asset,
                medium=medium_asset,
                original=original_asset,
            )

        bucket_name = settings.s3_bucket_name
        if not bucket_name:
            raise ServiceUnavailableError("S3 bucket is not configured. Verify S3_BUCKET_NAME.")

        expires_in = ttl_seconds or settings.s3_presigned_ttl_seconds
        expires_in = max(60, min(expires_in, 3600))
        preferred = preferred_variant if preferred_variant in {"thumb", "medium"} else "thumb"

        BotoCoreError, ClientError = self._get_s3_error_classes()
        try:
            s3_client = self._get_s3_client()
            variant_keys = self._build_variant_keys(normalized_storage_path)
            selected_key = variant_keys["thumb"] if preferred == "thumb" else variant_keys["medium"]

            selected_asset = self._build_signed_asset_for_key(
                s3_client=s3_client,
                bucket_name=bucket_name,
                key=selected_key,
                expires_in=expires_in,
            )
            thumb_asset = (
                selected_asset
                if selected_key == variant_keys["thumb"]
                else None
            )
            medium_asset = (
                selected_asset
                if selected_key == variant_keys["medium"]
                else None
            )
            original_asset = (
                selected_asset
                if selected_key == normalized_storage_path
                else None
            )
            return SignedAssetResponse(
                key=selected_asset.key,
                url=selected_asset.url,
                expires_at=selected_asset.expires_at,
                thumb=thumb_asset,
                medium=medium_asset,
                original=original_asset,
            )
        except (BotoCoreError, ClientError) as exc:
            raise ServiceUnavailableError(
                "Failed to generate signed URL for S3 image."
            ) from exc

    @staticmethod
    def extract_storage_key(value: str | None) -> str | None:
        if not value:
            return None

        raw_value = str(value).strip()
        if not raw_value:
            return None

        if raw_value.startswith("s3://"):
            parsed = raw_value[5:]
            slash_index = parsed.find("/")
            if slash_index == -1:
                return None
            return parsed[slash_index + 1 :].strip("/") or None

        if raw_value.startswith("http://") or raw_value.startswith("https://"):
            parsed = urlparse(raw_value)
            return ProviderStorageService._strip_media_prefix(parsed.path.lstrip("/")) or None

        return ProviderStorageService._strip_media_prefix(raw_value.lstrip("/")) or None

    def _validate_file(self, file: "UploadFile") -> None:
        if not file.filename:
            raise ApiError("Image file name is required")
        if file.content_type not in self.allowed_content_types:
            raise ApiError("Only JPG, PNG or WEBP images are allowed")

    def _build_webp_variants(self, content: bytes) -> dict[str, bytes]:
        try:
            with Image.open(BytesIO(content)) as image:
                converted_image = image.copy()
                if converted_image.mode not in {"RGB", "RGBA"}:
                    converted_image = converted_image.convert("RGBA")
                original = self._encode_webp(converted_image, quality=80)
                thumb = self._encode_webp(self._resize_for_width(converted_image, 480), quality=72)
                medium = self._encode_webp(self._resize_for_width(converted_image, 1080), quality=78)
                return {
                    "original": original,
                    "thumb": thumb,
                    "medium": medium,
                }
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ApiError("Invalid image file") from exc

    @staticmethod
    def _encode_webp(image: Image.Image, *, quality: int) -> bytes:
        output = BytesIO()
        image.save(output, format="WEBP", quality=quality, method=6)
        return output.getvalue()

    @staticmethod
    def _resize_for_width(image: Image.Image, max_width: int) -> Image.Image:
        width, height = image.size
        if width <= max_width:
            return image.copy()
        resized_height = max(1, int(round((height * max_width) / width)))
        return image.resize((max_width, resized_height), Image.Resampling.LANCZOS)

    @staticmethod
    def _build_variant_keys(storage_key: str) -> dict[str, str]:
        normalized_key = storage_key.lstrip("/")
        if "." in normalized_key:
            stem, _ext = normalized_key.rsplit(".", 1)
        else:
            stem = normalized_key
        filename = stem.rsplit("/", 1)[-1]
        folder = stem.rsplit("/", 1)[0] if "/" in stem else ""
        variants_folder = f"{folder}/variants" if folder else "variants"
        return {
            "thumb": f"{variants_folder}/{filename}_thumb.webp",
            "medium": f"{variants_folder}/{filename}_medium.webp",
        }

    def _build_signed_asset_for_key(
        self,
        *,
        s3_client: Any,
        bucket_name: str,
        key: str,
        expires_in: int,
    ) -> SignedAssetVariantResponse:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
        expires_at_iso = expires_at.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expires_in,
            HttpMethod="GET",
        )
        return SignedAssetVariantResponse(
            key=key,
            url=signed_url,
            expires_at=expires_at_iso,
        )

    def _build_variant_or_original_asset(
        self,
        *,
        s3_client: Any,
        bucket_name: str,
        variant_key: str,
        original_asset: SignedAssetVariantResponse,
        expires_in: int,
    ) -> SignedAssetVariantResponse:
        if self._object_exists(s3_client=s3_client, bucket_name=bucket_name, key=variant_key):
            return self._build_signed_asset_for_key(
                s3_client=s3_client,
                bucket_name=bucket_name,
                key=variant_key,
                expires_in=expires_in,
            )
        return original_asset

    def _build_local_asset_for_key(
        self,
        *,
        key: str,
        ttl_seconds: int | None,
    ) -> SignedAssetVariantResponse:
        settings = get_settings()
        expires_in = ttl_seconds or settings.s3_presigned_ttl_seconds
        expires_in = max(60, min(expires_in, 3600))
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
        expires_at_iso = expires_at.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return SignedAssetVariantResponse(
            key=key,
            url=self._build_local_asset_url(key),
            expires_at=expires_at_iso,
        )

    def _build_local_variant_or_original_asset(
        self,
        *,
        variant_key: str,
        original_asset: SignedAssetVariantResponse,
        ttl_seconds: int | None,
    ) -> SignedAssetVariantResponse:
        if self._local_object_exists(variant_key):
            return self._build_local_asset_for_key(key=variant_key, ttl_seconds=ttl_seconds)
        return original_asset

    @staticmethod
    def _object_exists(*, s3_client: Any, bucket_name: str, key: str) -> bool:
        _BotoCoreError, ClientError = ProviderStorageService._get_s3_error_classes()

        try:
            s3_client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as exc:
            status_code = str((exc.response or {}).get("ResponseMetadata", {}).get("HTTPStatusCode", ""))
            if status_code in {"403", "404"}:
                return False
            raise

    def _build_asset_url(self, storage_path: str) -> str:
        settings = get_settings()
        if settings.image_storage_backend == "local":
            return self._build_local_asset_url(storage_path)

        bucket_name = settings.s3_bucket_name
        region = settings.aws_region
        if not bucket_name or not region:
            raise ServiceUnavailableError(
                "S3 is not configured correctly. Verify S3_BUCKET_NAME and AWS_REGION."
            )

        public_base_url = settings.s3_public_base_url
        if public_base_url:
            normalized_base_url = public_base_url.rstrip("/")
            # Console URLs are not public asset links; ignore them and fallback.
            if (
                "console.aws.amazon.com" not in normalized_base_url
                and "/s3/buckets/" not in normalized_base_url
            ):
                return f"{normalized_base_url}/{storage_path}"

        return f"https://{bucket_name}.s3.{region}.amazonaws.com/{storage_path}"

    def _build_local_asset_url(self, storage_path: str) -> str:
        settings = get_settings()
        normalized_storage_path = storage_path.replace("\\", "/").lstrip("/")
        if settings.local_public_base_url:
            return f"{settings.local_public_base_url}/{normalized_storage_path}"
        media_path = settings.media_public_path.rstrip("/")
        return f"{media_path}/{normalized_storage_path}"

    def _get_s3_client(self):
        try:
            import boto3
        except ImportError as exc:
            raise ServiceUnavailableError(
                "S3 storage is deprecated in this branch and boto3 is not installed. Use IMAGE_STORAGE_BACKEND=local."
            ) from exc

        if self._s3_client_cached is not None:
            return self._s3_client_cached
        settings = get_settings()
        if not settings.s3_bucket_name or not settings.aws_region:
            raise ServiceUnavailableError(
                "S3 is not configured correctly. Verify S3_BUCKET_NAME and AWS_REGION."
            )

        client_kwargs: dict[str, str] = {"region_name": settings.aws_region}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        self._s3_client_cached = boto3.client("s3", **client_kwargs)
        return self._s3_client_cached

    def _upload_to_s3(self, storage_path: str, content: bytes) -> None:
        settings = get_settings()
        bucket_name = settings.s3_bucket_name
        if not bucket_name:
            raise ServiceUnavailableError("S3 bucket is not configured. Verify S3_BUCKET_NAME.")

        BotoCoreError, ClientError = self._get_s3_error_classes()
        try:
            s3_client = self._get_s3_client()
            s3_client.put_object(
                Bucket=bucket_name,
                Key=storage_path,
                Body=content,
                ContentType="image/webp",
                CacheControl="public,max-age=31536000,immutable",
            )
        except (BotoCoreError, ClientError) as exc:
            raise ServiceUnavailableError(
                "Failed to upload image to S3. Verify bucket permissions and AWS credentials."
            ) from exc

    def _upload_content(self, storage_path: str, content: bytes) -> None:
        settings = get_settings()
        if settings.image_storage_backend == "local":
            self._upload_to_local(storage_path, content)
            return
        self._upload_to_s3(storage_path, content)

    def _upload_to_local(self, storage_path: str, content: bytes) -> None:
        target_path = self._local_file_path(storage_path)
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(content)
        except OSError as exc:
            raise ServiceUnavailableError(
                "Failed to store image on the local server. Verify LOCAL_STORAGE_PATH permissions."
            ) from exc

    def _delete_from_s3(self, storage_path: str) -> None:
        settings = get_settings()
        bucket_name = settings.s3_bucket_name
        if not bucket_name:
            return

        BotoCoreError, ClientError = self._get_s3_error_classes()
        try:
            s3_client = self._get_s3_client()
            s3_client.delete_object(Bucket=bucket_name, Key=storage_path)
        except (BotoCoreError, ClientError):
            # Best effort cleanup: avoid failing request responses after DB mutation.
            return

    def _delete_content(self, storage_path: str) -> None:
        settings = get_settings()
        if settings.image_storage_backend == "local":
            self._delete_from_local(storage_path)
            return
        self._delete_from_s3(storage_path)

    def _delete_from_local(self, storage_path: str) -> None:
        try:
            self._local_file_path(storage_path).unlink(missing_ok=True)
        except OSError:
            # Best effort cleanup: avoid failing request responses after DB mutation.
            return

    def _local_object_exists(self, storage_path: str) -> bool:
        return self._local_file_path(storage_path).is_file()

    @staticmethod
    def local_storage_root() -> Path:
        settings = get_settings()
        configured_path = Path(settings.local_storage_path)
        if configured_path.is_absolute():
            return configured_path
        return Path(__file__).resolve().parents[2] / configured_path

    def _local_file_path(self, storage_path: str) -> Path:
        normalized_storage_path = storage_path.replace("\\", "/").lstrip("/")
        if not normalized_storage_path or ".." in Path(normalized_storage_path).parts:
            raise ApiError("Invalid image key")
        return self.local_storage_root() / normalized_storage_path

    @staticmethod
    def _strip_media_prefix(value: str) -> str:
        normalized_value = value.strip().lstrip("/")
        media_prefix = get_settings().media_public_path.strip("/")
        if media_prefix and normalized_value.startswith(f"{media_prefix}/"):
            return normalized_value[len(media_prefix) + 1 :]
        return normalized_value

    @staticmethod
    def _get_s3_error_classes():
        try:
            from botocore.exceptions import BotoCoreError, ClientError
        except ImportError as exc:
            raise ServiceUnavailableError(
                "S3 storage is deprecated in this branch and botocore is not installed. Use IMAGE_STORAGE_BACKEND=local."
            ) from exc
        return BotoCoreError, ClientError
