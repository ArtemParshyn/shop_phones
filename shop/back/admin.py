from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import User, Phone, Colors
from .widgets import ColoredCheckboxSelectMultiple


class PhoneAdminForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = '__all__'
        widgets = {
            'colors': ColoredCheckboxSelectMultiple,
        }


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    form = PhoneAdminForm
    list_display = ('name', 'price', 'brand')

    class Media:
        css = {
            'all': ('admin/css/color_admin.css',),
        }


@admin.register(Colors)
class ColorsAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'hex')

    def colored_name(self, obj):
        return format_html(
            '<span style="'
            'background-color: #{hex}; '
            'color: white; '
            'padding: 2px 5px; '
            'border-radius: 3px;'
            '">{title}</span>',
            hex=obj.hex,
            title=obj.title
        )

    colored_name.short_description = "Цвет"


# Остальные регистрации
admin.site.register(User)
