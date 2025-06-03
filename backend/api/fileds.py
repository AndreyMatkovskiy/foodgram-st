import base64
from django.core.files.base import ContentFile
from rest_framework import fields


class Base64ImageField(fields.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, data = data.split(';base64,')
            ext = header.split('/')[-1]
            if ext not in ['jpeg', 'jpg', 'png', 'gif']:
                ext = 'png'
            decoded_file = ContentFile(
                base64.b64decode(data),
                name=f'image.{ext}'
            )
            return super().to_internal_value(decoded_file)
        return super().to_internal_value(data)
