import json

from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from back.models import Phone, User
from tickets.models import Ticket, Message


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
        # try:
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


class TicketDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def get(self, request, ticket_id):
        ticket_from_request = get_object_or_404(Ticket, pk=ticket_id)
        if request.user != ticket_from_request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        messages = Message.objects.filter(ticket=ticket_from_request)

        answer = {
            "ticket": {
                "id": ticket_from_request.id,
                "subject": ticket_from_request.subject,
                "description": ticket_from_request.description,
                "status": ticket_from_request.status,
                "priority": ticket_from_request.priority,
                "created_at": ticket_from_request.created_at,
            },
            'messages': [
                {
                    'id': message.id,
                    'content': message.content,
                    'user': {
                        'id': message.user.id,
                        'name': message.user.username
                    },
                    'is_support': message.is_staff,
                    'created_at': message.created_at
                }
                for message in messages]
        }

        return Response(status=200, data=answer)


class MessagesAPI(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def get(self, request):
        ticket_from_request = get_object_or_404(Ticket, pk=request.GET.get('ticket', int))
        if request.user != ticket_from_request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        messages = Message.objects.filter(ticket=ticket_from_request)

        answer = {
            'messages': [
                {
                    'id': message.id,
                    'content': message.content,
                    'user': {
                        'id': message.user.id,
                        'name': message.user.username
                    },
                    'is_support': message.is_staff,
                    'created_at': message.created_at
                }
                for message in messages]
        }

        return Response(status=200, data=answer)

    def post(self, request):
        data = request.data
        ticket_from_request = get_object_or_404(Ticket, pk=data['ticket_id'])
        if request.user != ticket_from_request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket_from_request.status = 'pending'

        ticket_from_request.save()

        mess = Message.objects.create(content=data['content'],
                               user=request.user,
                               is_staff=False,
                               ticket=ticket_from_request)
        answer = {
            'messages':
                {
                    'id': mess.id,
                    'content': mess.content,
                    'user': {
                        'id': mess.user.id,
                        'name': mess.user.username
                    },
                    'is_support': mess.is_staff,
                    'created_at': mess.created_at
                }

        }

        return Response(status=status.HTTP_201_CREATED, data=answer)


class TicketCloseAPI(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def post(self, request, ticket_id):

        ticket_from_request = get_object_or_404(Ticket, pk=ticket_id)
        if request.user != ticket_from_request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket_from_request.status = 'closed'
        ticket_from_request.save()

        answer = {'success': True,
                  'ticket': {
                      'id': ticket_id,
                      'status': 'closed',
                  }}

        return Response(status=status.HTTP_201_CREATED, data=answer)
