from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.utils.decorators import decorator_from_middleware
import datetime
from utils.logger import *
from utils.extras import *
from utils.middleware import *
from django.db import transaction  # Add this at the top of your file

logger = setup_console_logger()

# Create your views here.
@api_view(['GET'])
@decorator_from_middleware(AuthenticationMiddleware)
def get_expense_details(request):
    expense_id = request.query_params.get('expense_id')
    user_id = request.COOKIES.get('user_id')

    created_by_me = Expense.objects.filter(created_by__user_id= int(user_id), expense_id=expense_id).exists()
    associated_with_me = Participant.objects.filter(user__user_id= int(user_id), expense__expense_id=expense_id).exists()

    if not (created_by_me or associated_with_me):
        return Response({
            'status': 'error',
            'message': 'You do not have access to this expense.',
            'status_code': status.HTTP_403_FORBIDDEN
        })

    try:
        expense = Expense.objects.get(expense_id=expense_id)
        participants = expense.participants.all()  # Using the related name

        data = {
            "description": expense.description,
            "total_amount": expense.total_amount,
            "split_method": expense.split_method,
            "created_at": expense.created_at,
            "total_participants": expense.total_user,  # Update to correct field
            "participants": [{"user_id": participant.user.user_id, "amount_paid": participant.amount_paid, "amount_owed": participant.amount_owed} for participant in participants]
        }

        return Response({
            'status': 'success',
            'message': "Expense retrieved successfully.",
            'status_code': status.HTTP_200_OK,
            'data': data,
        })

    except Expense.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Expense not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })

    
@api_view(['POST'])
@decorator_from_middleware(AuthenticationMiddleware)
def equalDistribution(request):
    
    # Extract user_id and email from cookies
    user_id = request.COOKIES.get('user_id')
    email_id = request.COOKIES.get('email')
    
    # Retrieve input data from the request
    user_list = request.data.get('user_list')  # List of user IDs involved
    total_amount = request.data.get('total_amount')  # Total expense amount
    description = request.data.get('description')  # Description of the expense
    
    # Ensure authentication data is present
    if not user_id or not email_id:
        response = {
            'status': 'error',
            'message': "Authentication Failed",
            'status_code': status.HTTP_400_BAD_REQUEST,
        }
        return Response(response)

    try:
        # Calculate equal share for each user
        each_user_share = round(total_amount / (len(user_list) * 1.0), 2)
        
        # Fetch the user who created the expense
        user = User.objects.get(user_id=user_id)
        
        # Add data to the Expense table
        expense_data = {
            'description': description,
            'total_amount': total_amount,
            'split_method': 'EQUAL',
            'created_by': user,
            'total_user': len(user_list)
        }
        expense = Expense.objects.create(**expense_data)
        
        # List to store participant details for the response
        participant_details = []

        # Loop through each user and create entries in the Participant table
        with transaction.atomic():  # Use transaction for database integrity
            for user_in_list in user_list:
                participant_user = User.objects.get(user_id=int(user_in_list['user_id']))
                amount_owed = each_user_share if participant_user.user_id != int(user_id) else 0  # Creator doesn't owe
                amount_paid = total_amount if participant_user.user_id == int(user_id) else 0  # Creator paid total

                # Create participant entry
                participant = Participant.objects.create(
                    expense=expense,
                    user=participant_user,
                    amount_paid=amount_paid,
                    amount_owed=amount_owed,
                    split_expenses = each_user_share
                )
                
                # Append participant details for the response
                participant_details.append({
                    'user_id': participant_user.user_id,
                    'user_name': participant_user.name,
                    'amount_paid': amount_paid,
                    'amount_owed': amount_owed
                })
        
        # Success response
        response = {
            'status': 'success',
            'message': 'Expense successfully added and split equally.',
            'expense_id': expense.expense_id,
            'description': expense.description,
            'total_amount': expense.total_amount,
            'split_method': expense.split_method,
            'each_user_share': each_user_share,
            "no_of_participants": len(user_list),
            'participants': participant_details
        }
        return Response(response, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })
    
    except Exception as e:
        # Handle any exceptions and return error response
        response = {
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return Response(response)


@api_view(['POST'])
@decorator_from_middleware(AuthenticationMiddleware)
def unequalDistribution(request):
    
    # Extract user_id and email from cookies
    user_id = request.COOKIES.get('user_id')
    email_id = request.COOKIES.get('email')
    
    # Retrieve input data from the request
    user_list = request.data.get('user_list')  # List of user IDs and their specific contributions
    total_amount = request.data.get('total_amount')  # Total expense amount
    description = request.data.get('description')  # Description of the expense
    
    # Validate the sum of user contributions
    sum = 0
    for user_amount in user_list:
        sum += float(user_amount["amount"])
    
    if round(sum, 2) != round(float(total_amount), 2):
        return Response({
            'status': 'error',
            'message': "Split does not sum up to the total amount. Please check.",
            'status_code': status.HTTP_400_BAD_REQUEST,
        })        
    
    # Ensure authentication data is present
    if not user_id or not email_id:
        response = {
            'status': 'error',
            'message': "Authentication Failed",
            'status_code': status.HTTP_400_BAD_REQUEST,
        }
        return Response(response)

    try:
        # Fetch the user who created the expense
        user = User.objects.get(user_id=user_id)
        
        # Add data to the Expense table
        expense_data = {
            'description': description,
            'total_amount': total_amount,
            'split_method': 'UNEQUAL',
            'created_by': user,
            'total_user': len(user_list),
        }
        expense = Expense.objects.create(**expense_data)
        
        # List to store participant details for the response
        participant_details = []

        # Loop through each user in the request and create entries in the Participant table
        with transaction.atomic():  # Use transaction for database integrity
            for participant_info in user_list:
                participant_user = User.objects.get(user_id= int(participant_info['user_id']))
                amount_paid = total_amount if participant_info['user_id'] == int(user_id) else 0  # Default to 0 if not provided
                amount_owed = 0 if participant_info['user_id'] == int(user_id) else participant_info.get('amount', 0)  # Default to 0 if not provided
                each_user_share = participant_info.get('amount', 0)
                
                # Create participant entry
                participant = Participant.objects.create(
                    expense=expense,
                    user=participant_user,
                    amount_paid=amount_paid,
                    amount_owed=amount_owed,
                    split_expenses = each_user_share
                )
                
                # Append participant details for the response
                participant_details.append({
                    'user_id': participant_user.user_id,
                    'user_name': participant_user.name,
                    'amount_paid': amount_paid,
                    'amount_owed': amount_owed,
                    'split_expenses': each_user_share
                })
        
        # Success response
        response = {
            'status': 'success',
            'message': 'Expense successfully added with custom splits.',
            'expense_id': expense.expense_id,
            'description': expense.description,
            'total_amount': expense.total_amount,
            'split_method': expense.split_method,
            'participants': participant_details
        }
        return Response(response, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })
        
    except Exception as e:
        # Handle any exceptions and return error response
        response = {
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return Response(response)

@api_view(['POST'])
@decorator_from_middleware(AuthenticationMiddleware)
def percentageDistribution(request):
    
    # Extract user_id and email from cookies
    user_id = request.COOKIES.get('user_id')
    email_id = request.COOKIES.get('email')
    
    # Retrieve input data from the request
    user_list = request.data.get('user_list')  # List of user IDs and their percentage shares
    total_amount = request.data.get('total_amount')  # Total expense amount
    description = request.data.get('description')  # Description of the expense
    
    # Ensure authentication data is present
    if not user_id or not email_id:
        return Response({
            'status': 'error',
            'message': "Authentication Failed",
            'status_code': status.HTTP_400_BAD_REQUEST
        })

    try:
        # Validate that the sum of percentages equals 100
        total_percentage = sum([participant['percentage'] for participant in user_list])
        if total_percentage != 100:
            return Response({
                'status': 'error',
                'message': 'Total percentages must add up to 100.',
                'status_code': status.HTTP_400_BAD_REQUEST
            })
        
        # Fetch the user who created the expense
        user = User.objects.get(user_id=user_id)
        
        # Add data to the Expense table
        expense_data = {
            'description': description,
            'total_amount': total_amount,
            'split_method': 'PERCENTAGE',
            'created_by': user,
            'total_user': len(user_list)
        }
        expense = Expense.objects.create(**expense_data)
        
        # List to store participant details for the response
        participant_details = []

        # Loop through each user in the request and create entries in the Participant table
        with transaction.atomic():  # Use transaction for database integrity
            for participant_info in user_list:
                participant_user = User.objects.get(user_id=participant_info['user_id'])
                
                # Calculate how much each participant owes based on their percentage
                percentage = participant_info.get('percentage', 0)  # Default to 0 if not provided
                amount_owed = 0 if participant_info['user_id'] == int(user_id) else round((percentage / 100) * total_amount, 2)  # Calculate based on percentage
                amount_paid = total_amount if participant_info['user_id'] == int(user_id) else 0  # User who created the expense might pay
                each_user_share = round((percentage / 100) * total_amount, 2)
                # Create participant entry
                participant = Participant.objects.create(
                    expense=expense,
                    user=participant_user,
                    amount_paid=amount_paid,
                    amount_owed=amount_owed,
                    split_expenses = each_user_share
                )
                
                # Append participant details for the response
                participant_details.append({
                    'user_id': participant_user.user_id,
                    'user_name': participant_user.name,
                    'percentage': percentage,
                    'amount_paid': amount_paid,
                    'amount_owed': amount_owed,
                    'split_expenses' : each_user_share
                })
        
        # Success response
        return Response({
            'status': 'success',
            'message': 'Expense successfully added with percentage-based splits.',
            'expense_id': expense.expense_id,
            'description': expense.description,
            'total_amount': expense.total_amount,
            'split_method': expense.split_method,
            'participants': participant_details
        }, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })
    
    except Exception as e:
        # Handle any exceptions and return error response
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })