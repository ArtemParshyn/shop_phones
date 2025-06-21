from django.urls import path
from back import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('register', views.register, name='register'),
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('shop', views.shop, name='shop'),
    path('devices', views.device, name='devices'),
    path('top_models', views.top_models, name='top_models'),
    path('faq', views.faq, name='faq'),
    path('tickets', views.tickets, name='tickets'),
    path('cart', views.cart, name='cart'),
    path('detailed/<int:phone_id>/', views.detailed, name='detailed'),
    path('proceed', views.proceed, name='proceed'),
    path('api/phones/<int:phone_id>/', views.phone_detail_api, name='phone_detail_api'),
    path('transaction', views.transaction, name='transaction'),

]


