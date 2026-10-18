"""Durable, bounded avatar storage for serverless deployments."""
from io import BytesIO
import uuid
import warnings

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import Storage, default_storage
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_AVATAR_BYTES = 3 * 1024 * 1024


@deconstructible
class ProfilePictureStorage(Storage):
    def _save(self, name, content):
        from app.models import ProfilePicture
        if content.size > MAX_AVATAR_BYTES:
            raise ValidationError('Choose an image smaller than 3 MB.')
        try:
            content.seek(0)
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(content) as original:
                    if original.format not in {'JPEG', 'PNG', 'WEBP', 'GIF'}:
                        raise ValidationError('Choose a JPEG, PNG, WebP, or GIF image.')
                    if original.width * original.height > 20_000_000:
                        raise ValidationError('Choose an image smaller than 20 megapixels.')
                    image = ImageOps.exif_transpose(original)
                    image.thumbnail((512, 512))
                    image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                    output = BytesIO()
                    image.save(output, format='WEBP', quality=85)
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise ValidationError('This image could not be read. Choose a valid image.') from exc
        picture = ProfilePicture.objects.create(content=output.getvalue())
        return f'avatars/{picture.pk}.webp'

    def _open(self, name, mode='rb'):
        from app.models import ProfilePicture
        if not name.startswith('avatars/'):
            return default_storage.open(name, mode)
        try:
            picture = ProfilePicture.objects.get(pk=self._picture_id(name))
        except (ProfilePicture.DoesNotExist, ValueError) as exc:
            raise FileNotFoundError(name) from exc
        return ContentFile(bytes(picture.content), name=name)

    @staticmethod
    def _picture_id(name):
        return uuid.UUID(name.removeprefix('avatars/').removesuffix('.webp'))

    def exists(self, name):
        from app.models import ProfilePicture
        if not name.startswith('avatars/'):
            return default_storage.exists(name)
        try:
            return ProfilePicture.objects.filter(pk=self._picture_id(name)).exists()
        except ValueError:
            return False

    def url(self, name):
        if name.startswith('avatars/'):
            return reverse('profile_picture', args=[self._picture_id(name)])
        return default_storage.url(name)

    def size(self, name):
        with self.open(name) as content:
            return content.size

    def delete(self, name):
        from app.models import ProfilePicture
        if name.startswith('avatars/'):
            ProfilePicture.objects.filter(pk=self._picture_id(name)).delete()

    def get_available_name(self, name, max_length=None):
        # The stored name is replaced by a fresh UUID on every upload.
        return name
