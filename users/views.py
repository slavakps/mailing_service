from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import UserRegisterForm
from .models import User


class UserRegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/profile.html"
    fields = ("username", "first_name", "last_name", "phone_number", "country", "avatar")

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("profile")