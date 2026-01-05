from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from .models import Client, Mailing, Message
from .services import send_mailing


@method_decorator(cache_page(60), name="dispatch")
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = "mailing/client_create.html"
    fields = ("email", "FIO", "comment")
    success_url = reverse_lazy("client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = "mailing/client_update.html"
    fields = ("email", "FIO", "comment")
    success_url = reverse_lazy("client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ("start_datetime", "end_datetime", "message", "recipients")
    template_name = "mailing/mailing_create.html"
    success_url = reverse_lazy("mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["start_datetime"].widget = forms.TextInput(
            attrs={
                "placeholder": "YYYY-MM-DD HH:MM",
                "class": "form-control",
            }
        )

        form.fields["end_datetime"].widget = forms.TextInput(
            attrs={
                "placeholder": "YYYY-MM-DD HH:MM",
                "class": "form-control",
            }
        )

        return form


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempt_set.order_by("-attempt_datetime")
        return context


@method_decorator(cache_page(60), name="dispatch")
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Mailing.objects.all().order_by("-start_datetime")
        return Mailing.objects.filter(owner=self.request.user).order_by(
            "-start_datetime"
        )


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = "mailing/mailing_update.html"
    fields = ("start_datetime", "end_datetime", "status", "message", "recipients")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("mailing_detail", kwargs={"pk": self.object.pk})


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("mailing_list")


@method_decorator(cache_page(60), name="dispatch")
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ("title", "body")
    template_name = "mailing/message_create.html"
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ("title", "body")
    template_name = "mailing/message_create.html"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("message_detail", kwargs={"pk": self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_delete.html"
    context_object_name = "message"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("message_list")


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            for mailing in Mailing.objects.filter(owner=user):
                mailing.update_status()

            context["all_mailings_count"] = Mailing.objects.filter(owner=user).count()
            context["active_mailings_count"] = Mailing.objects.filter(
                owner=user, status="started"
            ).count()
            context["unique_clients_count"] = Client.objects.filter(owner=user).count()
            context["show_stats"] = True

        else:
            context["show_stats"] = False

        return context


@login_required
def mailing_send_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    result = send_mailing(mailing)
    messages.success(request, f"Рассылка №{mailing.id}: {result}")
    return redirect("mailing_detail", pk=pk)