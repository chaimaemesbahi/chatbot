from django.db import models

class Incident(models.Model):
    description = models.TextField()
    sla = models.IntegerField()
    statut = models.CharField(max_length=50, default='En attente')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
