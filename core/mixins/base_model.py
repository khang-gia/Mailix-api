import uuid

from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import gettext as _
from django_softdelete.models import SoftDeleteModel

from core.mixins import SoftDeleteManager


class BaseModelMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metadata = models.JSONField(_("metadata"), null=True, blank=True, default=dict)
    is_deleted = models.BooleanField(_("is_deleted"), default=False)
    is_active = models.BooleanField(_("is_active"), default=True)
    created_at = models.DateTimeField(_("created_at"), editable=False, auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True, blank=True, null=True, editable=False)
    deleted_at = models.DateTimeField(_("deleted_at"), null=True, default=None, blank=True)

    objects = SoftDeleteManager()
    original_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(BaseModelMixin, self).delete()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    @property
    def get_instance_as_dict(self) -> dict:
        data = model_to_dict(self)
        data.setdefault("id", self.id)
        data.setdefault("created_at", self.created_at)
        data.setdefault("updated_at", self.updated_at)
        return dict(sorted(data.items()))



class BaseCreateDeleteModel(SoftDeleteModel):
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    is_archived = models.BooleanField('Is Archived', default=False)
    archived_at = models.DateTimeField('Archived At', auto_now = True, null=True)
    class Meta:
        abstract = True

class BaseCreateUpdateModel(BaseCreateDeleteModel):
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    class Meta:
        abstract = True
