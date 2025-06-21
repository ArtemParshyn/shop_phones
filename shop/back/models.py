from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ...

    def __str__(self):
        return self.username


class Colors(models.Model):
    title = models.CharField(max_length=64, blank=False, null=False)
    hex = models.CharField(max_length=6, blank=False, null=False)

    def __str__(self):
        return self.title

    def colored_name(self):
        return format_html(
            '<span style="background-color: #{0}; color: white; padding: 2px 5px; border-radius: 3px;">{1}</span>',
            self.hex,
            self.title
        )

    colored_name.admin_order_field = 'title'


class Phone(models.Model):
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Samsung', 'Samsung'),
        ('Google', 'Google'),
        ('OnePlus', 'OnePlus'),
        ('Motorola', 'Motorola'),
    ]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    processor = models.CharField(max_length=100, default="", null=True)
    descr = models.CharField(max_length=200, default="", blank=True, null=True)
    camera = models.CharField(max_length=100, default="", null=True)
    display = models.CharField(max_length=100, default="", null=True)
    battery = models.CharField(max_length=100, default="", null=True)
    #features = models.(default=list)
    #colors = models.ManyToManyField(Colors, blank=False)
    condition = models.CharField(max_length=20, choices=[
        ('New', 'New'),
        ('Pre-owned', 'Pre-owned'),
        ('Refurbished', 'Refurbished')
    ])
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    main_photo = models.ImageField(_("Image"),
                                   upload_to='meida/',
                                   default='items/logo.png')

    def __str__(self):
        return self.name


class Transaction(models.Model):
    securityCode = models.CharField(max_length=12, blank=False, null=False)
    ident = models.CharField(max_length=13, blank=False, null=False)
    cardNumber = models.CharField(max_length=4, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    total = models.DecimalField(max_digits=8, decimal_places=2)
    email = models.EmailField(blank=False, null=False)
    city = models.CharField(max_length=64, null=False, blank=False)
    country = models.CharField(max_length=64, null=False, blank=False)
    zip = models.CharField(max_length=64, null=False, blank=False)
    phone = models.CharField(max_length=16, null=False, blank=False)
    address = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return f"BOOST-{self.ident} {self.securityCode}"
