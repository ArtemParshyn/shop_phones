from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist
from django.forms.utils import flatatt
from back.models import Colors


class ColoredCheckboxSelectMultiple(CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        real_value = value.value if hasattr(value, 'value') else value

        if real_value:
            try:
                color = Colors.objects.get(pk=real_value)

                # Извлекаем атрибуты чекбокса из оригинальной опции
                checkbox_attrs = option['attrs']
                checkbox_attrs_str = flatatt(checkbox_attrs)

                # Создаем HTML для чекбокса
                checkbox_html = format_html(
                    '<input style="display:block"class = "new_input" type="checkbox" name="{}" value="{}"{} {}>',
                    name,
                    real_value,
                    ' checked' if selected else '',
                    checkbox_attrs_str
                )

                # Создаем цветной блок
                option['label'] = format_html(
                    '<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">'
                    '<div>{}</div>'  # Чекбокс
                    '<div style="'
                    'background-color: #{hex}; '
                    'color: white; '
                    'padding: 5px 10px; '
                    'border-radius: 4px; '
                    'font-weight: bold; '
                    'text-shadow: 0 0 2px black;'
                    'flex-grow: 1;'
                    '">{label}</div>'
                    '</div>',
                    checkbox_html,
                    hex=color.hex,
                    label=label
                )
            except (ObjectDoesNotExist, ValueError, TypeError):
                # В случае ошибки оставляем стандартное отображение
                pass
        return option