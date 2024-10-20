from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.utils.decorators import decorator_from_middleware
import datetime
from utils.logger import *
from utils.extras import *
from utils.middleware import *
from utils.generate_report import *
from django.db import transaction  # Add this at the top of your file
from expense.models import Expense, Participant, User  # Import your models
from django.http import HttpResponse
from utils import generate_report  # Assuming the PDF function is in utils.py

logger = setup_console_logger()

@api_view(['GET'])
@decorator_from_middleware(AuthenticationMiddleware)
def overallBalanceSheet(request):
    return None 


@api_view(['GET'])
@decorator_from_middleware(AuthenticationMiddleware)
def individualBalanceSheet(request):
    # Extract user_id from cookies
    user_id = request.COOKIES.get('user_id')
    
    # Ensure authentication data is present
    if not user_id:
        return Response({
            'status': 'error',
            'message': "Authentication Failed",
            'status_code': status.HTTP_400_BAD_REQUEST
        })
    
    try:
        user = User.objects.get(user_id=user_id)
        download = request.query_params.get('download', 'false').lower() == 'true'  
        # Fetch all participant records for the user, including related expenses
        participated_expenses = Participant.objects.filter(user=user).select_related('expense')

        # Initialize variables for totals
        total_expenses = 0  # Total amount the user has paid (their share of expenses)
        expenses_details = []
        
        total_own_expenses = 0
        total_owed_to_user = 0

        # Process participated expenses (user is a participant)
        for participant_exp in participated_expenses:
            expense = participant_exp.expense
            
            participants = Participant.objects.filter(expense=expense)
            for participant in participants:
                if participant.user != user:
                    total_owed_to_user += participant.amount_owed  # Sum the amount others owe to the user

            # Add user's share to the total
            total_expenses += expense.total_amount
            total_own_expenses += participant_exp.split_expenses
            
            # Add expense details to response
            expenses_details.append({
                'expense_id': expense.expense_id,
                'description': expense.description,
                'user_expense': participant_exp.split_expenses  # User's share of the expense
            })
        response_data = {
                'user_id': user.user_id,
                'total_expenses': total_expenses,  # Total amount paid by the user for all expenses
                'expenses': expenses_details,  # Detailed list of expenses
                'total_user_expenses': total_own_expenses,
                'total_owed_to_user': total_owed_to_user
            }
        if download:
            return generate_balance_sheet_pdf(response_data)
        else:
            # If no download, return the raw JSON data
            return Response(response_data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })