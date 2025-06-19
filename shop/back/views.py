import decimal
import math

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db import connection
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import login
from back import forms
import json


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

    return render(request, 'register.html', context={'auth': request.user.is_authenticated, 'form': form})


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


def shop(request):
    return render(request, template_name='shop.html', context={'auth': request.user.is_authenticated})


# views.py
from django.http import JsonResponse
from .models import Phone


def device(request):
    search_query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 6))
    sort_by = request.GET.get('sort', 'popular')
    print(request.GET)

    brands = [i.split(',') for i in request.GET.getlist('brands', [])][0]
    price_ranges = [i.split(',') for i in request.GET.getlist('priceRanges', [])][0]
    conditions = [i.split(',') for i in request.GET.getlist('conditions', [])][0]

    print(f"Надо найти: {search_query}")
    print(f"Сортировка по: {sort_by}")

    print(f"Бренды: {brands}")
    print(f"Ценики: {price_ranges}")
    print(f"Состояние: {conditions}")
    devices = Phone.objects.all()
    print(devices)

    # Фильтрация устройств
    if sort_by == 'price-low':
        devices = devices.order_by('price')

    elif sort_by == 'price-high':
        devices = devices.order_by('-price')

    elif sort_by == 'newest':
        print(11)
        devices = devices.order_by('-created_at')

    if any(brands):
        devices = devices.filter(brand__in=brands)
        print(devices)

    if any(conditions):
        devices = devices.filter(condition__in=conditions)
        print(devices)

    if price_ranges:
        # Парсинг диапазонов с поддержкой Decimal
        parsed_ranges = []
        for s in price_ranges:
            parts = s.split('-')
            try:
                if len(parts) == 1:
                    value = decimal.Decimal(parts[0].strip())
                    if value == 800:  # Особый случай
                        parsed_ranges.append((value, None))
                    else:
                        parsed_ranges.append((value, value))
                elif len(parts) == 2:
                    low = decimal.Decimal(parts[0].strip()) if parts[0].strip() else decimal.Decimal('0')
                    high = decimal.Decimal(parts[1].strip()) if parts[1].strip() else None
                    parsed_ranges.append((low, high))
            except (ValueError, decimal.InvalidOperation):
                continue

        # Сначала фильтруем по цене, потом по условиям
        price_query = Q()
        for low, high in parsed_ranges:
            if high is None:
                price_query |= Q(price__gte=low)
            elif low == high:
                price_query |= Q(price=low)
            else:
                price_query |= Q(price__gte=low, price__lte=high)

        devices = devices.filter(price_query)

    print(devices)

    # Применение фильтров...
    # Сортировка...
    # Пагинация...
    print(page, limit * page + 1)
    return JsonResponse({
        'total': len(devices),
        'devices': [{"name": i.name,
                     "price": i.price,
                     "processor": i.processor,
                     "display": i.display,
                     "camera": i.camera,
                     "battery": i.battery,
                     "image": i.main_photo.url} for i in devices[limit * page - 6:limit * page]]
    })


def top_models(request):
    devices = Phone.objects.all()
    devices = devices.order_by('rating')[:6]

    models = [{"name": i.name,
               "price": i.price,
               "processor": i.processor,
               "display": i.display,
               "camera": i.camera,
               "battery": i.battery,
               "rating": [i for i in range(math.floor(i.rating))],
               "descr": i.descr,
               "rating_half": bool(i.rating - math.floor(i.rating)),
               "image": i.main_photo.url} for i in devices]

    return render(request, template_name='top_models.html', context={'auth': request.user.is_authenticated, 'models': models[::-1]})


def faq(request):
    return render(request, template_name='faq.html',  context={'auth': request.user.is_authenticated})


def tickets(request):
    return render(request, template_name='ticket.html',  context={'auth': request.user.is_authenticated})
