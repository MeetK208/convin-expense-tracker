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
from django.db.models import Sum

logger = setup_console_logger()

@api_view(['GET'])
@decorator_from_middleware(AuthenticationMiddleware)
def overallBalanceSheet(request):
    try:
        logger.info("Received request for overall balance sheet")
        
        user_id = request.COOKIES.get('user_id')
        logger.debug(f"User ID from cookies: {user_id}")
        
        if not user_id:
            logger.error("User ID not found in cookies")
            return Response({
                'status': 'error',
                'message': 'Authentication failed: User ID not found.',
                'status_code': status.HTTP_400_BAD_REQUEST
            })
        
        user = User.objects.get(user_id=user_id)
        logger.info(f"User found: {user.name} ({user.email})")
        
        # Get all expenses where the user is a participant
        participant_expenses = Participant.objects.filter(user=user)
        logger.debug(f"Participant expenses retrieved for user: {len(participant_expenses)} records found")
        
        # Prepare the response data
        dashboard_data = {
            'user_id': user_id,
            'name': user.name,
            'email': user.email,
            'total_expenses_created': 0.0,
            'total_owed_by_user': 0.0,
            'total_paid_by_user': 0.0,
            'give_expenses': [],
            'get_expenses': []
        }
        
        for participant in participant_expenses:
            expense = participant.expense
            logger.debug(f"Processing expense ID: {expense.expense_id}, Description: {expense.description}")
            
            if expense.created_by == user:
                participants_owed = Participant.objects.filter(expense=expense).exclude(user=user)
                amount_paid_by_user = participant.amount_paid
                
                dashboard_data['total_expenses_created'] += float(expense.total_amount)
                dashboard_data['total_paid_by_user'] += float(amount_paid_by_user)
                
                participants_owes = [{'user_name': p.user.name, 'amount_owed': float(p.amount_owed)} for p in participants_owed]
                dashboard_data['get_expenses'].append({
                    'expense_id': expense.expense_id,
                    'description': expense.description,
                    'created_by': 'You',
                    'is_creator': True,
                    'total_paid': float(amount_paid_by_user),
                    'owes': participants_owes
                })
            else:
                creator = expense.created_by
                dashboard_data['total_owed_by_user'] += float(participant.amount_owed)
                
                dashboard_data['give_expenses'].append({
                    'expense_id': expense.expense_id,
                    'description': expense.description,
                    'created_by': creator.name,
                    'is_creator': False,
                    'total_owed': float(participant.amount_owed),
                    'give_to': {'user_name': creator.name, 'amount': float(participant.amount_owed)}
                })
        
        download = request.query_params.get('download', 'false').lower() == 'true'
        if download:
            logger.info("Generating PDF report for overall balance sheet")
            return generate_overall_balance_sheet_pdf(dashboard_data)
        else:
            logger.info("Returning overall balance sheet as JSON response")
            return Response(dashboard_data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        logger.error("User not found for the given user_id")
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })

    except Exception as e:
        logger.exception("An error occurred while processing the overall balance sheet")
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })

@api_view(['GET'])
@decorator_from_middleware(AuthenticationMiddleware)
def individualBalanceSheet(request):
    try:
        logger.info("Received request for individual balance sheet")
        
        # Extract user_id from cookies
        user_id = request.COOKIES.get('user_id')
        logger.debug(f"User ID from cookies: {user_id}")
        
        if not user_id:
            logger.error("User ID not found in cookies")
            return Response({
                'status': 'error',
                'message': "Authentication failed: User ID not found.",
                'status_code': status.HTTP_400_BAD_REQUEST
            })
        
        user = User.objects.get(user_id=user_id)
        logger.info(f"User found: {user.name} ({user.email})")
        
        # Fetch all participant records for the user, including related expenses
        participated_expenses = Participant.objects.filter(user=user).select_related('expense')
        logger.debug(f"Participated expenses retrieved: {len(participated_expenses)} records found")
        
        # Initialize variables for totals
        total_expenses = 0  # Total amount the user has paid (their share of expenses)
        expenses_details = []
        
        total_own_expenses = 0
        total_owed_to_user = 0

        # Process participated expenses (user is a participant)
        for participant_exp in participated_expenses:
            expense = participant_exp.expense
            logger.debug(f"Processing expense ID: {expense.expense_id}, Description: {expense.description}")
            
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
            'name': user.name,
            'email': user.email,
            'total_expenses': total_expenses,  # Total amount paid by the user for all expenses
            'expenses': expenses_details,  # Detailed list of expenses
            'total_user_expenses': total_own_expenses,
            'total_owed_to_user': total_owed_to_user
        }

        download = request.query_params.get('download', 'false').lower() == 'true'
        if download:
            logger.info("Generating PDF report for individual balance sheet")
            return generate_balance_sheet_pdf(response_data)
        else:
            logger.info("Returning individual balance sheet as JSON response")
            return Response(response_data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        logger.error("User not found for the given user_id")
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })

    except Exception as e:
        logger.exception("An error occurred while processing the individual balance sheet")
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })
      
