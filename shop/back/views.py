import decimal
import math
import random

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
from rest_framework import status

from back import forms
import json

from tickets.models import Ticket


def index(request):
    print(request.user.is_authenticated)
    a = random.randint(0, Phone.objects.all().count()-3)
    answer = {
        "auth": request.user.is_authenticated,
        'items': [{
            'image': i.main_photo.url,
            'name': i.name,
            'price': i.price,
            'processor': i.processor,
            'id': i.id,
            'display': i.display,
            'battery': i.battery,
            'camera': i.camera,
        } for i in Phone.objects.all()[a:a+3]]}
    return render(request, template_name='index.html', context=answer)


@login_required(login_url="register")
def profile(request):
    all_user_transactions = Transaction.objects.all().filter(user=request.user)
    print(all_user_transactions)
    all_user_transaction_count = all_user_transactions.count()
    amount = sum(i.total for i in all_user_transactions)
    tickets_user = Ticket.objects.all().filter(user=request.user, status='open').count()
    print(amount)
    print(tickets_user)
    return render(request, "profile.html", {
        "user": {'username': request.user.username,
                 'joined_at': request.user.date_joined.year,
                 'spent': amount,
                 'tickets': tickets_user,
                 'orders': all_user_transaction_count},
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
from .models import Phone, Transaction


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

    print(page, limit * page + 1)
    return JsonResponse({
        'total': len(devices),
        'devices': [{"name": i.name,
                     "id": i.id,
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
               "id": i.id,
               "price": i.price,
               "processor": i.processor,
               "display": i.display,
               "camera": i.camera,
               "battery": i.battery,
               "rating": [i for i in range(math.floor(i.rating))],
               "descr": i.descr,
               "rating_half": bool(i.rating - math.floor(i.rating)),
               "image": i.main_photo.url} for i in devices]

    return render(request, template_name='top_models.html',
                  context={'auth': request.user.is_authenticated, 'models': models[::-1]})


def faq(request):
    return render(request, template_name='faq.html', context={'auth': request.user.is_authenticated})


@login_required(login_url="register")
def tickets(request):
    return render(request, template_name='ticket.html', context={'auth': request.user.is_authenticated})


def cart(request):
    return render(request, template_name='cart.html', context={'auth': request.user.is_authenticated})


# views.py
from django.http import JsonResponse
from .models import Phone, Colors
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_GET
from django.conf import settings


def detailed(request, phone_id):
    phone = Phone.objects.all().get(id=phone_id)
    rel_phones = Phone.objects.order_by('-rating')
    answer = {'auth': request.user.is_authenticated,
              'phone': {"name": phone.name,
                        "price": phone.price,
                        "processor": phone.processor,
                        "display": phone.display,
                        "camera": phone.camera,
                        "battery": phone.battery,
                        "image": phone.main_photo.url,
                        "brand": phone.brand,
                        'condition': phone.condition,
                        'descr': phone.descr,
                        },
              'related_products': [
                  {
                      'name': i.name,
                      'image': i.main_photo.url,
                      'id': i.id,
                      'price': i.price
                  } for i in rel_phones[0:3]
              ]
              }
    print(rel_phones)
    # phones =
    return render(request, template_name='detailed.html', context=answer)


@require_GET
def phone_detail_api(request, phone_id):
    try:
        phone = Phone.objects.get(id=phone_id)

        # Получаем изображения телефона
        images = [request.build_absolute_uri(phone.main_photo.url)]  # Только главное фото

        # Получаем цвета
        colors = [
            {
                "id": color.id,
                "name": color.title,
                "hex": color.hex
            }
            for color in phone.colors.all()
        ]

        # Формируем характеристики
        specs = [
            {"icon": "fa-microchip", "title": "Processor", "text": phone.processor},
            {"icon": "fa-camera", "title": "Camera", "text": phone.camera},
            {"icon": "fa-mobile", "title": "Display", "text": phone.display},
            {"icon": "fa-battery-full", "title": "Battery", "text": phone.battery},
        ]

        # Добавляем дополнительные фичи
        for feature in phone.features:
            specs.append({
                "icon": "fa-star",
                "title": "Feature",
                "text": feature
            })

        # Получаем похожие товары (того же бренда)
        related_phones = Phone.objects.filter(
            brand=phone.brand
        ).exclude(id=phone.id)[:3]

        related_products = [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "image": request.build_absolute_uri(p.main_photo.url) if p.main_photo else ""
            }
            for p in related_phones
        ]

        return JsonResponse({
            "phone": {
                "id": phone.id,
                "name": phone.name,
                "description": phone.descr or "",
                "price": float(phone.price),
                "old_price": float(phone.price) * 1.1,  # 10% скидка
                "rating": phone.rating,
                "review_count": 1245,  # Статическое значение
                "main_image": request.build_absolute_uri(phone.main_photo.url) if phone.main_photo else "",
                "images": images,
                "colors": colors,
                "specs": specs
            },
            "related_products": related_products
        })

    except ObjectDoesNotExist:
        return JsonResponse({"error": "Phone not found"}, status=404)


def proceed(request):
    return render(request, template_name='proceed.html', context={'auth': request.user.is_authenticated})


def transaction(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            Transaction.objects.create(securityCode=data['securityCode'],
                                       ident=data['ident'],
                                       cardNumber=data['payment']['cardNumber'],
                                       user=request.user,
                                       total=data['total'],
                                       email=data['customer']['email'],
                                       city=data['customer']['city'],
                                       address=data['customer']['address'],
                                       country=data['customer']['country'],
                                       zip=data['customer']['zip'],
                                       phone=data['customer']['phone'],
                                       )

            return JsonResponse({'success': True})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
