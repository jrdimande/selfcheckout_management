from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.permissions import AdminRequiredMixin
from apps.audit.services import log, snapshot

SHARED = "selfcheckout"


class FilteredListView(LoginRequiredMixin, ListView):
    """Lista genérica com filtros GET, paginação e colunas declarativas."""
    paginate_by = 20
    template_name = "generic/list.html"
    title = ""
    columns = []          # (cabeçalho, caminho.do.atributo[, tipo])
    filter_form_class = None
    detail_url = edit_url = delete_url = create_url = None
    create_label = "Novo"

    def base_queryset(self):
        return self.model._default_manager.all()

    def apply_filters(self, qs, data):
        return qs

    def get_filter_form(self):
        return self.filter_form_class(self.request.GET or None) if self.filter_form_class else None

    def get_queryset(self):
        qs = self.base_queryset()
        form = self.get_filter_form()
        if form is not None and form.is_valid():
            qs = self.apply_filters(qs, form.cleaned_data)
        return qs

    def get_stats(self, qs):
        return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(title=self.title, columns=self.columns, form=self.get_filter_form(),
                   detail_url=self.detail_url, edit_url=self.edit_url, delete_url=self.delete_url,
                   create_url=self.create_url, create_label=self.create_label,
                   stats=self.get_stats(self.object_list))
        return ctx


class SaveView(AdminRequiredMixin):
    template_name = "generic/form.html"
    db = SHARED
    title = ""
    cancel_url = None
    success_message = "Guardado com sucesso."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(title=self.title, cancel_url=self.cancel_url)
        return ctx

    def form_valid(self, form):
        creating = self.object is None
        with transaction.atomic(using=self.db):
            self.object = form.save()
        log(self.request, "create" if creating else "update", self.object,
            getattr(self, "_before", None), snapshot(self.object))
        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())


class CreateRecord(SaveView, CreateView):
    pass


class UpdateRecord(SaveView, UpdateView):
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self._before = snapshot(obj)
        return obj


class DeleteRecord(AdminRequiredMixin, View):
    model = None
    db = SHARED
    success_url_name = None
    http_method_names = ["post"]

    def post(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        blocker = obj.deletion_blocker()
        if blocker:
            messages.error(request, blocker)
            return redirect(obj.get_absolute_url())
        before, label = snapshot(obj), str(obj)
        with transaction.atomic(using=self.db):
            obj.delete()
        log(request, "delete", obj, before, None, object_id=pk, object_repr=label)
        messages.success(request, f"«{label}» eliminado.")
        return redirect(self.success_url_name)
