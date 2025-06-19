import json

from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from back.models import Phone, User
from tickets.models import Ticket


# Create your views here.
class TicketsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получаем параметры фильтрации из запроса
        status_filter = request.query_params.get('status', 'all').lower()
        priority_filter = request.query_params.get('priority', 'all').lower()
        date_filter = request.query_params.get('date', None)
        print(status_filter, priority_filter)
        # Фильтрация тикетов по пользователю
        tickets = Ticket.objects.filter(user=request.user)

        # Применяем фильтры
        if status_filter != 'all':
            tickets = tickets.filter(status=status_filter)
        if priority_filter != 'all':
            tickets = tickets.filter(priority=priority_filter)
        if date_filter:
            tickets = tickets.filter(created_at__date=date_filter)

        # Форматируем данные для ответа
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'subject': ticket.subject,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat(),
            })

        return Response({'tickets': tickets_data}, status=status.HTTP_200_OK)

    def post(self, request):
        #try:
        data = request.data
        # Валидация
        required_fields = ['subject', 'description', 'priority', 'category']
        print(data)
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        # Создание тикета
        ticket = Ticket.objects.create(
            user=request.user,
            subject=data['subject'],
            description=data['description'],
            priority=data['priority'],
            status='open'
        )
        print(ticket)
        return Response({
            'id': ticket.id,
            'subject': ticket.subject,
            # ... другие поля ...
        }, status=status.HTTP_201_CREATED)

        #except Exception as e:
        #    return Response(
        #        {'error': str(e)},
        #        status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #    )

class TicketDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, int):
        print()
        return Response(status=200, data={'message': 1})
