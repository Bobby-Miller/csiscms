from django.conf.urls import url
from . import views

urlpatterns= [
    url(
        r'^(?P<doc_type>[a-zA-Z]+)/add/$',
        views.DocumentCreate.as_view(),
        name='document_add'
    ),
]