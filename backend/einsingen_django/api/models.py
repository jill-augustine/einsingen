# from .api.models import *

from django.conf import settings
from django.db import models as db_models


class UserOptions(db_models.Model):
    user = db_models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=db_models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name="options",
    )

    is_guest = db_models.BooleanField(default=False)
