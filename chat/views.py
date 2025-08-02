from rest_framework.decorators import api_view
from rest_framework.response import Response
from interventions.models import Incident

# Structure d'état de la conversation
user_states = {}

@api_view(['POST'])
def chatbot_view(request):
    message = request.data.get('message', '').strip().lower()
    user_id = request.data.get('user_id', 'default')  # pour gérer plusieurs utilisateurs

    if user_id not in user_states:
        user_states[user_id] = {"state": "initial", "description": "", "duree": ""}

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
            "response": "Tu peux donner la description de l'incident.",
        })

    if state["state"] == "awaiting_description":
        state["description"] = message
        state["state"] = "awaiting_duree"
        return Response({
            "response": "Quelle est la durée estimée pour résoudre cet incident ?"
        })

    if state["state"] == "awaiting_duree":
        state["duree"] = message

        # Création de l'incident
        Incident.objects.create(description=state["description"], sla=state["duree"])

        # Réinitialisation
        user_states[user_id] = {"state": "initial", "description": "", "duree": ""}

        return Response({
            "response": "Incident bien enregistré avec succès ✅",
            "refresh": True  # pour que React déclenche le rafraîchissement
        })

    return Response({
        "response": "Je n'ai pas compris. Essayez : Bonjour",
        "suggestions": [
            {"label": "Bonjour", "value": "Bonjour"}
        ]
    })
