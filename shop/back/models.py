from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import format_html


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
    ch = [
        ("Iphone", "IPhone"),
        ("Samsung", "Samsung"),
        ("Xiaomi", "Xiaomi"),
        ("Redmi", "Redmi"),
        ("Honor", "Honor")
    ]

    title = models.CharField(max_length=64, blank=False, null=False)
    cost = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False, default=0)
    model = models.CharField(choices=ch, max_length=64, blank=False, null=False, default=False)
    colors = models.ManyToManyField(Colors, blank=False)

    def __str__(self):
        return self.title
