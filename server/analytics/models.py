from django.db import models
from django.conf import settings


class Query(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="queries"
    )
    message = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Query by {self.user.email} at {self.created_at}"


class BudgetUsage(models.Model):
    date = models.DateField(auto_now_add=True)
    total_queries = models.IntegerField(default=0)
    gcp_cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Budget for {self.date}: ${self.gcp_cost_estimate}"
