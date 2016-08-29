from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse


class DocType(models.Model):
    doc_type = models.CharField(max_length=64, unique=True)


class DocStatus(models.Model):
    doc_status = models.CharField(max_length=32, unique=True)


class ControlledDoc(models.Model):
    doc_type = models.ForeignKey(to=DocType, on_delete=models.CASCADE, to_field='doc_type')
    doc_status = models.ForeignKey(to=DocStatus, on_delete=models.CASCADE, to_field='doc_status')
    document = models.FileField()
    uploaded_by = models.ForeignKey(to=settings.ACCOUNTS_PROFILE_MODEL, on_delete=models.SET_NULL, null=True)
    upload_datetime = models.DateTimeField()
    last_used = models.DateTimeField(null=True)

    def get_absolute_url(self):
        return reverse('doc_control:doc', kwargs={'doc_type': self.doc_type})