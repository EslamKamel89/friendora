import uuid

from django.utils.text import slugify


def unique_slug(text: str) -> str:
    """
    Generate a unique slug based on text.
    """
    base_slug = slugify(text)
    unique_id = uuid.uuid4().hex[:6]
    return f"{base_slug}-{unique_id}"
