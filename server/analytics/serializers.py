from rest_framework import serializers


class AnalyticsSerializer(serializers.Serializer):
    total_queries = serializers.IntegerField()
    total_documents = serializers.IntegerField()
    total_users = serializers.IntegerField()
    recent_queries = serializers.IntegerField()
    documents = serializers.ListField()
