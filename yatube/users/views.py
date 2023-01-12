from django.views.generic import CreateView
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.urls import reverse_lazy


from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class ChangePass(CreateView):
    form_class = PasswordChangeForm
    success_url: str = reverse_lazy('users:password_change_done')
    template_name: str = 'users/password_change_form.html'


class ResetPass(CreateView):
    form_class = PasswordResetForm
    success_url: str = reverse_lazy('users:password_reset_done')
    template_name: str = 'users/password_reset_form.html'
