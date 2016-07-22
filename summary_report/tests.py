from django.test import TestCase
from datetime import datetime, date
from .models import Batch, Summary, TestPassPercent, MeasurementMean

# Create your tests here.

class BatchModelTests(TestCase):

    def test_duplicates_have_one_instance(self):
        """
        Batch_id was set to unique. Testing that duplicates are thrown out.
        Update: Unique alone allowed duplicate entries. Made batch_id PK to get desired
        output.
        """
        batch = 'test'
        batch = Batch(batch_id=batch)
        batch.save()
        batch = 'test'
        batch = Batch(batch_id=batch)
        batch.save()
        batch_list = [batch.batch_id for batch in Batch.objects.all()]
        self.assertEqual(batch_list, ['test',])


class SummaryAids:

    @staticmethod
    def value_entry_dict(value):
        return {('inspected', 'good', 'good_percent', 'fail_general', 'fail_gen_percent',
                 'fail_od', 'fail_od_percent', 'fail_backward', 'fail_backward_percent',
                 'n_a', 'n_a_percent'): value}

    @staticmethod
    def today_test_dict():
        return {'batch_id': 'test', 'date': date.today(), 'time': datetime.now().time()}
