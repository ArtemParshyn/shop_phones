from django.contrib import admin

from tickets.models import Ticket, Message


# Register your models here.

class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'description', 'user', 'status', 'created_at', 'priority')
    list_filter = ('user', 'created_at', 'status', 'priority')
    search_fields = ('subject', 'user__username', 'priority')
    list_display_links = ('subject', 'user')
    ordering = ('-created_at',)
    list_per_page = 25
    raw_id_fields = ('user',)
    status = ['mark_answered']

    #def save_model(self, request, obj, form, change):
    #    if change:
    #        original_obj = Ticket.objects.get(pk=obj.pk)
    #        if obj.answear != original_obj.answear and obj.answear.strip() != '':
    #            obj.status = True
    #    else:
    #        if obj.answear.strip() != '':
    #            obj.status = True
    #    super().save_model(request, obj, form, change)

    #def mark_answered(self, request, queryset):
    #    queryset.update(status=True)

    #mark_answered.short_description = "Mark selected tickets as answered"


admin.site.register(Ticket, TicketAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'user', 'ticket', 'created_at', 'is_staff')
    list_filter = ('user', 'created_at', 'is_staff', 'ticket')
    search_fields = ('content', 'user__username')
    list_display_links = ('user', 'ticket', 'content')
    ordering = ('-created_at',)
    list_per_page = 25
    raw_id_fields = ('user',)
    status = ['mark_answered']

    def save_model(self, request, obj, form, change):
        # При сохранении сообщения обновляем статус тикета
        if not change:
            obj.is_staff = request.user.is_staff

        super().save_model(request, obj, form, change)

        # Обновляем статус тикета при добавлении нового сообщения
        if not change and obj.ticket:
            ticket = obj.ticket

            ticket.status = 'open'
            ticket.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('ticket', 'user')


admin.site.register(Message, MessageAdmin)
