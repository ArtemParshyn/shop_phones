from django.urls import path
from tickets.views import TicketsAPI, TicketDetailAPI

urlpatterns = [
    path('', TicketsAPI.as_view(), name='tickets'),
    path('tickets/<int:ticket_id>/', TicketDetailAPI.as_view(), name='ticket-detail'),

]
