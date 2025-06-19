from django.urls import path
from tickets.views import TicketsAPI, TicketDetailAPI, MessagesAPI, TicketCloseAPI

app_name = 'tickets'


urlpatterns = [
    path('', TicketsAPI.as_view(), name='tickets'),
    path('<int:ticket_id>/', TicketDetailAPI.as_view(), name='ticket-detail'),
    path('messages/', MessagesAPI.as_view(), name='messages'),
    path('<int:ticket_id>/close/', TicketCloseAPI.as_view(), name='close-ticket'),
]
