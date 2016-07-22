from django.contrib import admin
from .models import Batch, Summary, TestPassPercent, MeasurementMean, MeasurementCount, \
    StandardID, MeasurementStandard, MeasurementCorrection

admin.site.register(Batch)
admin.site.register(Summary)
admin.site.register(TestPassPercent)
admin.site.register(MeasurementMean)
admin.site.register(MeasurementCount)
admin.site.register(StandardID)
admin.site.register(MeasurementStandard)
admin.site.register(MeasurementCorrection)