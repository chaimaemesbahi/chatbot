from rest_framework.decorators import api_view
from rest_framework.response import Response
from interventions.models import Incident
from datetime import datetime

# Structure d'état de la conversation
user_states = {}

@api_view(['POST'])
def chatbot_view(request):
    message = request.data.get('message', '').strip().lower()
    user_id = request.data.get('user_id', 'default')  # pour gérer plusieurs utilisateurs

    if user_id not in user_states:
        user_states[user_id] = {"state": "initial", "description": "", "duree": 0}

    state = user_states[user_id]

    if message == "bonjour":
        return Response({
            "response": "Bonjour, comment puis-je t'aider ?",
            "suggestions": [
                {"label": "Je veux créer un incident", "value": "Je veux créer un incident"}
            ]
        })

    if message == "je veux créer un incident":
        state["state"] = "awaiting_description"
        return Response({
            "response": "Tu peux donner la description de l'incident."
        })

    if state["state"] == "awaiting_description":
        state["description"] = request.data.get('message')  # garde le texte original
        state["state"] = "awaiting_duree"
        return Response({
            "response": "Quelle est la durée estimée pour résoudre cet incident SLA ?"
        })

    if state["state"] == "awaiting_duree":
        try:
            sla = int(request.data.get('message'))
        except ValueError:
            return Response({
                "response": "⛔ Merci de saisir un nombre entier pour la durée (ex: 4)."
            })

        state["duree"] = sla

        # ✅ Création de l'incident
        try:
            Incident.objects.create(
                description=state["description"],
                sla=state["duree"],
                date_creation=datetime.now(),
                statut="En attente",
                utilisateur_id=1  # à adapter selon ton app
            )
        except Exception as e:
            return Response({
                "response": f"❌ Erreur lors de la création de l'incident : {str(e)}"
            })

        # 🔁 Réinitialisation
        user_states[user_id] = {"state": "initial", "description": "", "duree": 0}

        return Response({
            "response": "✅ Incident bien enregistré avec succès !",
            "created": True
        })

    return Response({
        "response": "Je n'ai pas compris. Essayez : Bonjour",
        "suggestions": [
            {"label": "Bonjour", "value": "Bonjour"}
        ]
    })
