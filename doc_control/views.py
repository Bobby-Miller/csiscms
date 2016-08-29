from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import ControlledDoc, DocType
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime


@method_decorator(login_required, name='dispatch')
class DocumentCreate(CreateView):
    model = ControlledDoc
    fields = ['document', 'doc_status',]
    template_name = 'doc_control/document_add.html'

    def get_context_data(self, **kwargs):
        self.doc_type = get_object_or_404(DocType, doc_type=self.kwargs['doc_type'])
        return super(DocumentCreate, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.doc_type = self.doc_type.doc_type
        form.instance.uploaded_by = self.request.user
        form.upload_datetime = datetime.now()
        return super(DocumentCreate, self).form_valid(form)
