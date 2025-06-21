from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import User, Phone, Colors, Transaction
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


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'securityCode', 'ident', 'cardNumber', 'user', 'total')
    list_filter = ('user',)
    search_fields = ('securityCode', 'user__username', 'ident')
    list_display_links = ('user',)
    list_per_page = 25
    raw_id_fields = ('user',)


# Остальные регистрации
admin.site.register(User)
admin.site.register(Transaction, TransactionAdmin)
