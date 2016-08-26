from django.views import generic
from .models import Summary, MeasurementMean, MeasurementCount, TestPassPercent
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from itertools import chain


class Years(generic.ListView):
    template_name = 'summary_report/years.html'
    context_object_name = 'distinct_years'

    def get_queryset(self):
        distinct_entries = Summary.objects.dates('date', 'year')
        return [entry.year for entry in distinct_entries]

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Years, self).dispatch(*args, **kwargs)


class ReportYearArchiveView(generic.YearArchiveView):
    template_name = 'summary_report/months.html'
    queryset = Summary.objects.all()
    date_field = "date"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReportYearArchiveView, self).dispatch(*args, **kwargs)


class ReportMonthArchiveView(generic.ListView):
    context_object_name = 'batches'
    template_name = 'summary_report/month_summary.html'

    def get_queryset(self):
        query_year = self.kwargs['year']
        query_month = self.kwargs['month']

        batch_query = (Summary.objects
                       .filter(date__year=query_year, date__month=query_month)
                       .distinct('batch_id'))
        return batch_query

    def get_context_data(self, **kwargs):
        context = super(ReportMonthArchiveView, self).get_context_data(**kwargs)
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReportMonthArchiveView, self).dispatch(*args, **kwargs)


class BatchSummaryView(generic.ListView):
    template_name = 'summary_report/batch_summary.html'
    context_object_name = 'summary_data'

    def get_queryset(self):
        query_batch = self.kwargs['batch']

        summary_query = (Summary.objects.filter(batch_id=query_batch))
        return summary_query

    def get_context_data(self, **kwargs):
        context = super(BatchSummaryView, self).get_context_data(**kwargs)
        context['batch'] = self.kwargs['batch']
        summaries = (Summary.objects.filter(batch_id=self.kwargs['batch']))
        sum_map = {
            'sum_inspected': 'inspected',
            'sum_good': 'good',
            'sum_fail_gen': 'fail_general',
            'sum_fail_od': 'fail_od',
            'sum_fail_backward': 'fail_backward',
            'sum_n_a': 'n_a',
        }
        if summaries.exists():
            for summary in summaries:
                for sum_key, attr_val in sum_map.items():
                    if sum_key not in context:
                        context[sum_key] = getattr(summary, attr_val)
                    else:
                        context[sum_key] += getattr(summary, attr_val)
            for sum_key in sum_map.keys():
                context[sum_key+'_percent'] = context[sum_key]/context['sum_inspected'] * 100
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BatchSummaryView, self).dispatch(*args, **kwargs)


@login_required
def stats(request, category, batch, segment):
    # filters is used to map url category to django object query: {category: filter_kwargs}
    filters = {
        'inspected': {},
        'good': {'overall_result': 'Good'},
        'fail': {'overall_result': 'Fail'},
        'fail_od': {'overall_result': 'Fail - OD Envelope'},
        'fail_backward': {'overall_result': 'backwards'},
        'fail_na': {'overall_result': 'N/A'},
    }

    # add remaining filter elements to kwargs
    for filter_dict in filters.values():
        if segment:
            filter_dict['summary'] = segment
        else:
            pass
        filter_dict['batch_id'] = batch

    # Pull report instances
    means_instances = (MeasurementMean.objects
                       .filter(**filters[category])
                       .select_related('summary').all())
    counts_instances = (MeasurementCount.objects
                        .filter(**filters[category])
                        .select_related('summary').all())
    tests_instances = (TestPassPercent.objects
                       .filter(**filters[category])
                       .select_related('summary').all())

    # weight_map used to determine weight of measurement/test when averaging.
    weight_map = {
        'Good': 'good',
        'Fail': 'fail_general',
        'Fail - OD Envelope': 'fail_od',
        'Backwards': 'fail_backward',
        'N/A': 'n_a',
    }

    # Get list of fields to average in MeasurementMeans and TestPasses
    mean_fields = set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in MeasurementMean._meta.get_fields()
    ))
    test_fields = set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in TestPassPercent._meta.get_fields()
    ))

    # Discard non-value fields
    discard_fields = ('id', 'summary', 'overall_result', 'batch', 'batch_id', 'summary_id')
    for field in discard_fields:
        mean_fields.discard(field)
        test_fields.discard(field)

    # Building counts totals for each field
    counts_dict = {field: 0 for field in mean_fields}
    for instance in counts_instances:
        for field in mean_fields:
            counts_dict[field] += getattr(instance, field)

    # Means dict will hold the normalized value of each field calculated.
    means_dict = {field: 0 for field in mean_fields}
    for instance in means_instances:
        # Pull the counts instance associated with this means instance
        counts_instance = counts_instances.get(
            batch_id=instance.batch_id, summary=instance.summary,
            overall_result=instance.overall_result
        )
        for field in mean_fields:
            # The value to be normalized
            instance_val = getattr(instance, field)
            # The count (weight) of this instance
            instance_count = getattr(counts_instance, field)
            # The calculation
            try:
                normalized_val = instance_val * instance_count / counts_dict[field]
            except ZeroDivisionError:
                normalized_val = 0
            means_dict[field] += normalized_val

    # Because we don't factor out non-zero values for tests, the count is easier to gather.
    tests_count_sum = 0
    summary_id = None
    for instance in tests_instances:
        # Get the count from the summary value
        tests_count_sum += getattr(instance.summary, weight_map[instance.overall_result])
        summary_id = instance.summary

    # Normalize the tests averages
    tests_dict = {field: 0 for field in test_fields}
    for instance in tests_instances:
        for field in test_fields:
            instance_val = getattr(instance, field)
            instance_weight = getattr(instance.summary,
                                      weight_map[instance.overall_result])
            try:
                normalized_val = instance_val * instance_weight / tests_count_sum
            except ZeroDivisionError:
                normalized_val = 0
            tests_dict[field] += normalized_val

    # Dividing up fields by station

    round_means_fields = [
        'round_inner_bright_area',
        'round_outer_bright_area',
        'round_inner_small_dark_area',
        'round_outer_small_dark_area',
        'round_inner_large_dark_area',
        'round_outer_large_dark_area',
    ]

    round_tests_fields = [
        'round_end',
        'round_valid_master',
        'round_present',
        'round_orientation',
        'round_inner_bright',
        'round_outer_bright',
        'round_inner_small_dark',
        'round_outer_small_dark',
        'round_inner_large_dark',
        'round_outer_large_dark',
    ]

    round_readable_dict = {
        'round_inner_bright': 'Bright - Inner',
        'round_outer_bright': 'Bright - Outer',
        'round_inner_small_dark': 'Small Dark - Inner',
        'round_outer_small_dark': 'Small Dark - Outer',
        'round_inner_large_dark': 'Large Dark - Inner',
        'round_outer_large_dark': 'Large Dark - Outer',
        'round_inner_bright_area': 'Bright - Inner',
        'round_outer_bright_area': 'Bright - Outer',
        'round_inner_small_dark_area': 'Small Dark - Inner',
        'round_outer_small_dark_area': 'Small Dark - Outer',
        'round_inner_large_dark_area': 'Large Dark - Inner',
        'round_outer_large_dark_area': 'Large Dark - Outer',
        'round_end': 'Station',
        'round_valid_master': 'Valid - Master',
        'round_present': 'Present',
        'round_orientation': 'Orientation',
    }

    round_means_read_fields = []
    round_means_values = []
    round_means_counts = []
    for field in round_means_fields:
        round_means_read_fields.append(round_readable_dict[field])
        round_means_values.append(means_dict[field])
        round_means_counts.append(counts_dict[field])

    round_tests_read_fields = []
    round_tests_values = []
    for field in round_tests_fields:
        round_tests_read_fields.append(round_readable_dict[field])
        round_tests_values.append(tests_dict[field])

    round_context = {'means_fields': round_means_read_fields,
                     'means_values': round_means_values,
                     'counts': round_means_counts,
                     'tests_fields': round_tests_read_fields,
                     'tests_values': round_tests_values,
                     }

    flat_means_fields = [
        'flat_inner_diameter_min',
        'flat_inner_diameter_max',
        'flat_obstruction_area',
        'flat_chip_area',
    ]

    flat_tests_fields = [
        'flat_end',
        'flat_valid_master',
        'flat_orientation',
        'flat_valid',
        'flat_ID',
        'flat_obstruction',
        'flat_chip',
    ]

    flat_readable_dict = {
        'flat_inner_diameter_min': 'ID - Min',
        'flat_inner_diameter_max': 'ID - Max',
        'flat_obstruction_area': 'Obstruction Area',
        'flat_chip_area': 'Chip Area',
        'flat_end': 'Station',
        'flat_valid_master': 'Valid - Master',
        'flat_orientation': 'Orientation',
        'flat_valid': 'Valid',
        'flat_ID': 'ID',
        'flat_obstruction': 'Obstruction',
        'flat_chip': 'Chip',
    }

    flat_means_read_fields = []
    flat_means_values = []
    flat_means_counts = []
    for field in flat_means_fields:
        flat_means_read_fields.append(flat_readable_dict[field])
        flat_means_values.append(means_dict[field])
        flat_means_counts.append(counts_dict[field])

    flat_tests_read_fields = []
    flat_tests_values = []
    for field in flat_tests_fields:
        flat_tests_read_fields.append(flat_readable_dict[field])
        flat_tests_values.append(tests_dict[field])

    flat_context = {'means_fields': flat_means_read_fields,
                    'means_values': flat_means_values,
                    'counts': flat_means_counts,
                    'tests_fields': flat_tests_read_fields,
                    'tests_values': flat_tests_values,
                    }

    dimension_means_fields = [
        'dimension_envelope_mm',
        'dimension_median_od',
        'dimension_bump_max',
        'dimension_chip_max',
        'dimension_nose_min_max',
        'dimension_length_mm',
    ]

    dimension_tests_fields = [
        'outer_dimension',
        'dimension_position',
        'dimension_length',
        'dimension_bumps',
        'dimension_chips',
        'dimension_envelope',
        'dimension_nose',
    ]

    dimension_readable_dict = {
        'dimension_envelope_mm': 'Envelope',
        'dimension_envelope': 'Envelope',
        'dimension_median_od': 'OD - Median',
        'dimension_bump_max': 'Bump - Max',
        'dimension_chip_max': 'Chip - Max',
        'dimension_nose_min_max': 'Nose - Min/Max',
        'dimension_length_mm': 'Length',
        'dimension_length': 'Length',
        'outer_dimension': 'Station',
        'dimension_position': 'Position',
        'dimension_bumps': 'Bumps',
        'dimension_chips': 'Chips',
        'dimension_nose': 'Nose'
    }

    dimension_means_read_fields = []
    dimension_means_values = []
    dimension_means_counts = []
    for field in dimension_means_fields:
        dimension_means_read_fields.append(dimension_readable_dict[field])
        dimension_means_values.append(means_dict[field])
        dimension_means_counts.append(counts_dict[field])

    dimension_tests_read_fields = []
    dimension_tests_values = []
    for field in dimension_tests_fields:
        dimension_tests_read_fields.append(dimension_readable_dict[field])
        dimension_tests_values.append(tests_dict[field])

    dimension_context = {'means_fields': dimension_means_read_fields,
                         'means_values': dimension_means_values,
                         'counts': dimension_means_counts,
                         'tests_fields': dimension_tests_read_fields,
                         'tests_values': dimension_tests_values,
                         }

    cosmetic_means_fields = [
        'sepia_bright_area',
        'sepia_blemish_area',
        'sepia_spot_crack_area',
    ]

    cosmetic_tests_fields = [
        'sepia_screen',
        'sepia_valid',
        'sepia_bright_spot',
        'sepia_blemish',
        'sepia_spot_crack',
    ]

    cosmetic_readable_dict = {
        'sepia_bright_area': 'Bright Area',
        'sepia_blemish_area': 'Blemish Area',
        'sepia_spot_crack_area': 'Crack Area',
        'sepia_screen': 'Station',
        'sepia_valid': 'Valid',
        'sepia_bright_spot': 'Bright Spot',
        'sepia_blemish': 'Blemish',
        'sepia_spot_crack': 'Crack',
    }

    cosmetic_means_read_fields = []
    cosmetic_means_values = []
    cosmetic_means_counts = []
    for field in cosmetic_means_fields:
        cosmetic_means_read_fields.append(cosmetic_readable_dict[field])
        cosmetic_means_values.append(means_dict[field])
        cosmetic_means_counts.append(counts_dict[field])

    cosmetic_tests_read_fields = []
    cosmetic_tests_values = []
    for field in cosmetic_tests_fields:
        cosmetic_tests_read_fields.append(cosmetic_readable_dict[field])
        cosmetic_tests_values.append(tests_dict[field])

    cosmetic_context = {'means_fields': cosmetic_means_read_fields,
                        'means_values': cosmetic_means_values,
                        'counts': cosmetic_means_counts,
                        'tests_fields': cosmetic_tests_read_fields,
                        'tests_values': cosmetic_tests_values,
                        }

    category_display_map = {
        'inspected': 'All Sensors',
        'good': 'Good',
        'fail': 'Failed (General)',
        'fail_od': 'Failed (OD)',
        'fail_backward': 'Failed (Backwards)',
        'fail_na': 'Sensors Not Found/Not Valid',
    }
    display_category = category_display_map[category]

    # Rename segment if segment is None (which happens for job total reports)
    segment = 'Job Total' if not segment else summary_id

    return render(request, 'summary_report/report.html', {'round': round_context,
                                                          'flat': flat_context,
                                                          'dimension': dimension_context,
                                                          'cosmetic': cosmetic_context,
                                                          'batch': batch,
                                                          'segment': segment,
                                                          'category': display_category,
                                                          'count': tests_count_sum,
                                                          })