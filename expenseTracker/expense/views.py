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
    logger.info("Processing equal distribution for expense")
    
    user_id = request.COOKIES.get('user_id')
    email_id = request.COOKIES.get('email')
    
    user_list = request.data.get('user_list')
    total_amount = request.data.get('total_amount')
    description = request.data.get('description')

    if not user_id or not email_id:
        logger.error("Authentication failed. User ID or email missing from cookies")
        return Response({
            'status': 'error',
            'message': "Authentication failed.",
            'status_code': status.HTTP_400_BAD_REQUEST,
        })

    try:
        each_user_share = round(total_amount / (len(user_list) * 1.0), 2)
        user = User.objects.get(user_id=user_id)
        
        expense_data = {
            'description': description,
            'total_amount': total_amount,
            'split_method': 'EQUAL',
            'created_by': user,
            'total_user': len(user_list)
        }
        expense = Expense.objects.create(**expense_data)
        
        participant_details = []

        with transaction.atomic():
            for user_in_list in user_list:
                participant_user = User.objects.get(user_id=int(user_in_list['user_id']))
                amount_owed = each_user_share if participant_user.user_id != int(user_id) else 0
                amount_paid = total_amount if participant_user.user_id == int(user_id) else 0

                participant = Participant.objects.create(
                    expense=expense,
                    user=participant_user,
                    amount_paid=amount_paid,
                    amount_owed=amount_owed,
                    split_expenses=each_user_share
                )
                
                participant_details.append({
                    'user_id': participant_user.user_id,
                    'user_name': participant_user.name,
                    'amount_paid': amount_paid,
                    'amount_owed': amount_owed
                })

        logger.info(f"Equal expense added successfully. Expense ID: {expense.expense_id}")
        return Response({
            'status': 'success',
            'message': 'Expense added and split equally among participants.',
            'expense_id': expense.expense_id,
            'description': expense.description,
            'total_amount': expense.total_amount,
            'split_method': expense.split_method,
            'each_user_share': each_user_share,
            "no_of_participants": len(user_list),
            'participants': participant_details
        }, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        logger.error("User not found during equal distribution.")
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })
    
    except Exception as e:
        logger.exception("An error occurred during equal distribution")
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })


@api_view(['POST'])
@decorator_from_middleware(AuthenticationMiddleware)
def unequalDistribution(request):
    
    # Extract user_id and email from cookies
    user_id = request.COOKIES.get('user_id')
    email_id = request.COOKIES.get('email')
    logger.info(f"Request received for unequalDistribution by user {user_id}.")

    # Retrieve input data from the request
    user_list = request.data.get('user_list')  # List of user IDs and their specific contributions
    total_amount = request.data.get('total_amount')  # Total expense amount
    description = request.data.get('description')  # Description of the expense
    logger.debug(f"Input data: user_list={user_list}, total_amount={total_amount}, description={description}")
    
    # Validate the sum of user contributions
    total_contributions = sum(float(user_amount["amount"]) for user_amount in user_list)
    
    if round(total_contributions, 2) != round(float(total_amount), 2):
        logger.error("Total split does not match the total amount.")
        return Response({
            'status': 'error',
            'message': "The sum of user contributions does not match the total amount. Please check.",
            'status_code': status.HTTP_400_BAD_REQUEST,
        })        
    
    # Ensure authentication data is present
    if not user_id or not email_id:
        logger.warning("Authentication failed: Missing user_id or email.")
        return Response({
            'status': 'error',
            'message': "Authentication failed. Please log in and try again.",
            'status_code': status.HTTP_400_BAD_REQUEST,
        })

    try:
        # Fetch the user who created the expense
        user = User.objects.get(user_id=user_id)
        logger.info(f"User {user_id} found. Proceeding to create the expense.")

        # Add data to the Expense table
        expense_data = {
            'description': description,
            'total_amount': total_amount,
            'split_method': 'UNEQUAL',
            'created_by': user,
            'total_user': len(user_list),
        }
        expense = Expense.objects.create(**expense_data)
        logger.info(f"Expense created with ID: {expense.expense_id}")

        # List to store participant details for the response
        participant_details = []

        # Loop through each user in the request and create entries in the Participant table
        with transaction.atomic():  # Use transaction for database integrity
            for participant_info in user_list:
                participant_user = User.objects.get(user_id=int(participant_info['user_id']))
                amount_paid = total_amount if participant_info['user_id'] == int(user_id) else 0
                amount_owed = 0 if participant_info['user_id'] == int(user_id) else participant_info.get('amount', 0)
                each_user_share = participant_info.get('amount', 0)
                
                # Create participant entry
                participant = Participant.objects.create(
                    expense=expense,
                    user=participant_user,
                    amount_paid=amount_paid,
                    amount_owed=amount_owed,
                    split_expenses=each_user_share
                )
                
                # Append participant details for the response
                participant_details.append({
                    'user_id': participant_user.user_id,
                    'user_name': participant_user.name,
                    'amount_paid': amount_paid,
                    'amount_owed': amount_owed,
                    'split_expenses': each_user_share
                })
                logger.debug(f"Participant added: {participant_user.user_id}, amount_owed={amount_owed}, amount_paid={amount_paid}")

        # Success response
        response = {
            'status': 'success',
            'message': 'Expense successfully recorded with custom splits.',
            'expense_id': expense.expense_id,
            'description': expense.description,
            'total_amount': expense.total_amount,
            'split_method': expense.split_method,
            'participants': participant_details
        }
        logger.info("Expense and participant details successfully saved.")
        return Response(response, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        logger.error(f"User with user_id {user_id} not found.")
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })
        
    except Exception as e:
        # Handle any exceptions and return error response
        logger.exception("An error occurred while processing the request.")
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })


@api_view(['POST'])
@decorator_from_middleware(AuthenticationMiddleware)
def percentageDistribution(request):
    
    # Extract user_id and email from cookies
    user_id = request.COOKIES.get('user_id')
    email_id = request.COOKIES.get('email')
    logger.info(f"Request received for percentageDistribution by user {user_id}.")

    # Retrieve input data from the request
    user_list = request.data.get('user_list')  # List of user IDs and their percentage contributions
    total_amount = request.data.get('total_amount')  # Total expense amount
    description = request.data.get('description')  # Description of the expense
    logger.debug(f"Input data: user_list={user_list}, total_amount={total_amount}, description={description}")
    
    # Validate the total percentage sum
    total_percentage = sum(float(user_percentage["percentage"]) for user_percentage in user_list)
    
    if round(total_percentage, 2) != 100.00:
        logger.error("Total percentages do not add up to 100%.")
        return Response({
            'status': 'error',
            'message': "The total of percentages does not add up to 100%. Please check.",
            'status_code': status.HTTP_400_BAD_REQUEST,
        })
    
    # Ensure authentication data is present
    if not user_id or not email_id:
        logger.warning("Authentication failed: Missing user_id or email.")
        return Response({
            'status': 'error',
            'message': "Authentication failed. Please log in and try again.",
            'status_code': status.HTTP_400_BAD_REQUEST,
        })

    try:
        # Fetch the user who created the expense
        user = User.objects.get(user_id=user_id)
        logger.info(f"User {user_id} found. Proceeding to create the expense.")

        # Add data to the Expense table
        expense_data = {
            'description': description,
            'total_amount': total_amount,
            'split_method': 'PERCENTAGE',
            'created_by': user,
            'total_user': len(user_list),
        }
        expense = Expense.objects.create(**expense_data)
        logger.info(f"Expense created with ID: {expense.expense_id}")

        # List to store participant details for the response
        participant_details = []

        # Loop through each user in the request and create entries in the Participant table
        with transaction.atomic():  # Use transaction for database integrity
            for participant_info in user_list:
                participant_user = User.objects.get(user_id=int(participant_info['user_id']))
                each_user_share = (float(participant_info['percentage']) / 100) * float(total_amount)
                amount_paid = total_amount if participant_info['user_id'] == int(user_id) else 0
                amount_owed = each_user_share if participant_info['user_id'] != int(user_id) else 0
                
                # Create participant entry
                participant = Participant.objects.create(
                    expense=expense,
                    user=participant_user,
                    amount_paid=amount_paid,
                    amount_owed=amount_owed,
                    split_expenses=each_user_share
                )
                
                # Append participant details for the response
                participant_details.append({
                    'user_id': participant_user.user_id,
                    'user_name': participant_user.name,
                    'percentage': participant_info['percentage'],
                    'amount_paid': amount_paid,
                    'amount_owed': amount_owed,
                    'split_expenses': each_user_share
                })
                logger.debug(f"Participant added: {participant_user.user_id}, amount_owed={amount_owed}, amount_paid={amount_paid}")

        # Success response
        response = {
            'status': 'success',
            'message': 'Expense successfully recorded with percentage-based splits.',
            'expense_id': expense.expense_id,
            'description': expense.description,
            'total_amount': expense.total_amount,
            'split_method': expense.split_method,
            'participants': participant_details
        }
        logger.info("Expense and participant details successfully saved.")
        return Response(response, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        logger.error(f"User with user_id {user_id} not found.")
        return Response({
            'status': 'error',
            'message': 'User not found.',
            'status_code': status.HTTP_404_NOT_FOUND
        })
        
    except Exception as e:
        # Handle any exceptions and return error response
        logger.exception("An error occurred while processing the request.")
        return Response({
            'status': 'error',
            'message': str(e),
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })

    
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