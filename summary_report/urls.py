from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.Years.as_view(), name='years'),
    url(r'^(?P<year>[0-9]{4})/$',
        views.ReportYearArchiveView.as_view(),
        name='report_year_archive',
        ),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
        views.ReportMonthArchiveView.as_view(),
        name='month_report_list',
        ),
    url(r'^batch/(?P<batch>[A-Za-z0-9]+)/$',
        views.BatchSummaryView.as_view(),
        name='batch_summary',
        ),
    url(
        r'^stats/(?P<category>[A-Za-z\-]+)/(?P<batch>[A-Za-z0-9]+)/(?P<segment>[0-9]+)/$',
        views.stats,
        name='stats_report',
    ),
    url(r'^stats/(?P<category>[A-Za-z\-]+)/(?P<batch>[A-Za-z0-9]+)/$',
        views.stats,
        kwargs={'segment': None},
        name='total_stats_report',
    )
]