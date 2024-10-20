# from rest_framework import serializers
# from .models import Expense, Participant, Balance

# # Serializer for the Expense model
# class ExpenseSerializer(serializers.ModelSerializer):
#     participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # For linking participants

#     class Meta:
#         model = Expense
#         fields = ['expense_id', 'description', 'total_amount', 'split_method', 'created_by', 'created_at', 'total_user', 'participants']  # Include participants for linking

# # Serializer for the Participant model
# class ParticipantSerializer(serializers.ModelSerializer):
#     expense = serializers.PrimaryKeyRelatedField(read_only=True)  # To show expense ID
#     user = serializers.StringRelatedField()  # To show username instead of user ID

#     class Meta:
#         model = Participant
#         fields = ['participant_id', 'expense', 'user', 'amount_paid', 'amount_owed', 'percentage']

# # Serializer for the Balance model
# class BalanceSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField()  # To show username instead of user ID
#     owes_user = serializers.StringRelatedField()  # To show username instead of user ID

#     class Meta:
#         model = Balance
#         fields = ['balance_id', 'user', 'owes_user', 'amount', 'last_updated']
