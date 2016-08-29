from django.contrib import admin
from . import models


admin.site.register(models.DocType)
admin.site.register(models.DocStatus)
admin.site.register(models.ControlledDoc)
