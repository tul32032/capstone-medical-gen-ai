from rest_framework import serializers


class AnalyticsSerializer(serializers.Serializer):
    total_queries = serializers.IntegerField()
    total_documents = serializers.IntegerField()
    total_users = serializers.IntegerField()
    gcp_budget_used = serializers.DecimalField(max_digits=10, decimal_places=2)
    recent_queries = serializers.IntegerField()
    documents = serializers.ListField()
