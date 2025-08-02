from django.db import models

class Incident(models.Model):
    description = models.TextField()
    date_creation = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="en attente")  # exemple : "en attente", "en cours", "terminé"
    sla = models.IntegerField(help_text="Durée maximale (en heures) pour résoudre l'incident")
    utilisateur_id = models.IntegerField()  # à remplacer par une ForeignKey si tu as un modèle User

    def __str__(self):
        return f"Incident #{self.id} - {self.statut}"
