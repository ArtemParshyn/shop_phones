from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import login
from back import forms


def index(request):
    print(request.user.is_authenticated)
    return render(request, template_name='index.html', context={"auth": request.user.is_authenticated})


@login_required(login_url="register")
def profile(request):
    return render(request, "profile.html", {
        "user": request.user,
        "auth": True
    })


def register(request):
    if request.method == 'POST':
        form = forms.CustomUserCreationForm(request.POST)
        if form.is_valid():
            print(1)
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = forms.CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = forms.CustomLoginForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('index')


def logout_view(request):
    logout(request)
    return redirect('index')
