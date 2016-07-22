from django.db import models
from django.db.migrations.operations import RenameField


class Batch(models.Model):
    batch_id = models.CharField(max_length=31, primary_key=True, unique=True)

    def __str__(self):
        return self.batch_id

    class Meta:
        verbose_name_plural = 'batches'


class Summary(models.Model):
    batch = models.ForeignKey(to=Batch, on_delete=models.CASCADE, to_field='batch_id')
    date = models.DateField()
    time = models.TimeField()
    inspected = models.IntegerField()
    good = models.IntegerField()
    good_percent = models.DecimalField(max_digits=5, decimal_places=2)
    fail_general = models.IntegerField()
    fail_gen_percent = models.DecimalField(max_digits=5, decimal_places=2)
    fail_od = models.IntegerField()
    fail_od_percent = models.DecimalField(max_digits=5, decimal_places=2)
    fail_backward = models.IntegerField()
    fail_backward_percent = models.DecimalField(max_digits=5, decimal_places=2)
    n_a = models.IntegerField()
    n_a_percent = models.DecimalField(max_digits=5, decimal_places=2)
    gate_homes = models.IntegerField()
    lost_homing = models.IntegerField()

    class Meta:
        verbose_name_plural = 'summaries'

    def __str__(self):
        return str(self.date) + ' - ' + str(self.time)


class TestPassPercent(models.Model):
    batch = models.ForeignKey(to=Batch, on_delete=models.CASCADE)
    summary = models.ForeignKey(to=Summary, on_delete=models.CASCADE)
    overall_result = models.CharField(max_length=63)
    round_end = models.DecimalField(max_digits=5, decimal_places=2) # re_station
    flat_end = models.DecimalField(max_digits=5, decimal_places=2) # fe_station
    outer_dimension = models.DecimalField(max_digits=5, decimal_places=2) # odp_station
    sepia_screen = models.DecimalField(max_digits=5, decimal_places=2) # ss_station
    round_valid_master = models.DecimalField(max_digits=5, decimal_places=2) # re_valid_master
    round_valid = models.DecimalField(max_digits=5, decimal_places=2) # re_valid
    round_present = models.DecimalField(max_digits=5, decimal_places=2) # re_present
    round_orientation = models.DecimalField(max_digits=5, decimal_places=2) # re_orientation
    round_inner_bright = models.DecimalField(max_digits=5, decimal_places=2) # re_inner_bright
    round_outer_bright = models.DecimalField(max_digits=5, decimal_places=2) # re_outer_bright
    round_inner_small_dark = models.DecimalField(max_digits=5, decimal_places=2) # re_inner_small_dark
    round_outer_small_dark = models.DecimalField(max_digits=5, decimal_places=2) # re_outer_small_dark
    round_inner_large_dark = models.DecimalField(max_digits=5, decimal_places=2) # re_inner_large_dark
    round_outer_large_dark = models.DecimalField(max_digits=5, decimal_places=2) # re_outer_large_dark
    flat_valid_master = models.DecimalField(max_digits=5, decimal_places=2) # fe_valid_master
    flat_orientation = models.DecimalField(max_digits=5, decimal_places=2) # fe_orientation
    flat_valid = models.DecimalField(max_digits=5, decimal_places=2) # fe_valid
    flat_ID = models.DecimalField(max_digits=5, decimal_places=2) # fe_inner_diameter
    flat_obstruction = models.DecimalField(max_digits=5, decimal_places=2) # fe_obstruction
    flat_chip = models.DecimalField(max_digits=5, decimal_places=2) # fe_chip
    dimension_position = models.DecimalField(max_digits=5, decimal_places=2) # odp_position
    dimension_length = models.DecimalField(max_digits=5, decimal_places=2) # odp_length
    dimension_bumps = models.DecimalField(max_digits=5, decimal_places=2) # odp_bumps
    dimension_chips = models.DecimalField(max_digits=5, decimal_places=2) # odp_chips
    dimension_envelope = models.DecimalField(max_digits=5, decimal_places=2) # odp_envelope
    dimension_nose = models.DecimalField(max_digits=5, decimal_places=2) # odp_nose
    sepia_valid = models.DecimalField(max_digits=5, decimal_places=2) # ss_valid
    sepia_bright_spot = models.DecimalField(max_digits=5, decimal_places=2) # ss_bright_defect
    sepia_blemish = models.DecimalField(max_digits=5, decimal_places=2) # ss_blemish_defect
    sepia_spot_crack = models.DecimalField(max_digits=5, decimal_places=2) # ss_spot_crack_defect

    def __str__(self):
        return str(self.summary) + ' - ' + str(self.overall_result)


class MeasurementMean(models.Model):
    batch = models.ForeignKey(to=Batch, on_delete=models.CASCADE)
    summary = models.ForeignKey(to=Summary, on_delete=models.CASCADE)
    overall_result = models.CharField(max_length=63)
    round_inner_bright_area = models.FloatField() # re_ida_bright
    round_inner_large_dark_area = models.FloatField() # re_ida_large_dark
    round_inner_small_dark_area = models.FloatField() # re_ida_small_dark
    round_outer_bright_area = models.FloatField() # re_oda_bright
    round_outer_large_dark_area = models.FloatField() # re_oda_large_dark
    round_outer_small_dark_area = models.FloatField() # re_oda_small_dark
    flat_inner_diameter_min = models.FloatField() # fe_inner_dia_min
    flat_inner_diameter_max = models.FloatField() # fe_inner_dia_max
    flat_obstruction_area = models.FloatField() # fe_obstr_area
    flat_chip_area = models.FloatField() # fe_chip_area
    dimension_length_mm = models.FloatField() # odp_length_mm
    dimension_bump_max = models.FloatField() # odp_max_bump_mm
    dimension_chip_max = models.FloatField() # odp_max_chip_mm
    dimension_envelope_mm = models.FloatField() # odp_envelope_mm
    dimension_nose_min_max = models.FloatField() # odp_nose_w_min_max
    dimension_median_od = models.FloatField() # odp_mdn_od_mm
    sepia_bright_area = models.FloatField() # ss_bright_da_mm2
    sepia_blemish_area = models.FloatField() # ss_blemish_da_mm2
    sepia_spot_crack_area = models.FloatField() # ss_spot_crack_da_mm2

    def __str__(self):
        return (str(self.batch_id) + ' - '
                + str(self.summary) + ' - '
                + str(self.overall_result))


class MeasurementCount(models.Model):
    batch = models.ForeignKey(to=Batch, on_delete=models.CASCADE)
    summary = models.ForeignKey(to=Summary, on_delete=models.CASCADE)
    overall_result = models.CharField(max_length=63)
    round_inner_bright_area = models.IntegerField()  # re_ida_bright
    round_inner_large_dark_area = models.IntegerField()  # re_ida_large_dark
    round_inner_small_dark_area = models.IntegerField()  # re_ida_small_dark
    round_outer_bright_area = models.IntegerField()  # re_oda_bright
    round_outer_large_dark_area = models.IntegerField()  # re_oda_large_dark
    round_outer_small_dark_area = models.IntegerField()  # re_oda_small_dark
    flat_inner_diameter_min = models.IntegerField()  # fe_inner_dia_min
    flat_inner_diameter_max = models.IntegerField()  # fe_inner_dia_max
    flat_obstruction_area = models.IntegerField()  # fe_obstr_area
    flat_chip_area = models.IntegerField()  # fe_chip_area
    dimension_length_mm = models.IntegerField()  # odp_length_mm
    dimension_bump_max = models.IntegerField()  # odp_max_bump_mm
    dimension_chip_max = models.IntegerField()  # odp_max_chip_mm
    dimension_envelope_mm = models.IntegerField()  # odp_envelope_mm
    dimension_nose_min_max = models.IntegerField()  # odp_nose_w_min_max
    dimension_median_od = models.IntegerField()  # odp_mdn_od_mm
    sepia_bright_area = models.IntegerField()  # ss_bright_da_mm2
    sepia_blemish_area = models.IntegerField()  # ss_blemish_da_mm2
    sepia_spot_crack_area = models.IntegerField()  # ss_spot_crack_da_mm2

    def __str__(self):
        return (str(self.batch_id) + ' - '
                + str(self.summary) + ' - '
                + str(self.overall_result))


class StandardID(models.Model):
    group_name = models.CharField(max_length=31, unique=True)

    def __str__(self):
        return self.group_name


class MeasurementStandard(models.Model):
    standard_id = models.ForeignKey(to=StandardID, on_delete=models.CASCADE)
    measurement = models.CharField(max_length=31)
    min = models.FloatField(blank=True)
    max = models.FloatField(blank=True)
    nominal = models.FloatField(blank=True)

    def __str__(self):
        return self.measurement


class MeasurementCorrection(models.Model):
    measurement = models.CharField(max_length=31)
    correction_factor = models.FloatField()

    def __str__(self):
        return self.measurement