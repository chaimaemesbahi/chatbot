from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.db import connection

# État utilisateur
user_states = {}

@api_view(['POST'])
def chatbot_view(request):
    message = request.data.get('message', '').strip().lower()
    user_id = request.data.get('user_id', 'default')

    if user_id not in user_states:
        user_states[user_id] = {
            "state": "initial",
            "description": "",
            "duree": 0,
            "technicien": ""
        }

    state = user_states[user_id]

    # Étape 1 : Bonjour
    if message == "bonjour":
        return Response({
            "response": "Bonjour, comment puis-je t'aider ?",
            "suggestions": [
                {"label": "Je veux créer un incident", "value": "Je veux créer un incident"}
            ]
        })

    # Étape 2 : Choix de création
    if message == "je veux créer un incident":
        state["state"] = "awaiting_description"
        return Response({
            "response": "Tu peux donner la description de l'incident."
        })

    # Étape 3 : Description
    if state["state"] == "awaiting_description":
        state["description"] = request.data.get('message')
        state["state"] = "awaiting_duree"
        return Response({
            "response": "Quelle est la durée estimée pour résoudre cet incident (SLA en heures) ?"
        })

    # Étape 4 : SLA
    if state["state"] == "awaiting_duree":
        try:
            state["duree"] = int(request.data.get('message'))
        except ValueError:
            return Response({"response": "⛔ Merci d’entrer un nombre entier pour la durée (ex: 4)."})

        state["state"] = "awaiting_technicien"
        return Response({
            "response": "Quel technicien doit être assigné ? (ex: Ali, Samir)",
            "suggestions": [
                {"label": "Ali", "value": "Ali"},
                {"label": "Samir", "value": "Samir"}
            ]
        })

    # Étape 5 : Technicien (optionnel)
    if state["state"] == "awaiting_technicien":
        technicien_nom = request.data.get('message')
        technicien_id = None

        if technicien_nom:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM techniciens WHERE LOWER(nom) = LOWER(%s) LIMIT 1",
                        [technicien_nom]
                    )
                    result = cursor.fetchone()
                    if result:
                        technicien_id = result[0]
            except Exception as e:
                return Response({"response": f"⚠️ Erreur technicien : {str(e)}"})

        try:
            # Création incident
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO incident (description, date_creation, statut, utilisateur_id, sla)
                    VALUES (%s, NOW(), %s, %s, %s)
                """, [state["description"], 'ouvert', 1, state["duree"]])

                incident_id = cursor.lastrowid  # récupérer ID

            # Création intervention liée
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO intervention (date_intervention, description, incident_id, statut, technicien_id, sla)
                    VALUES (NOW(), %s, %s, %s, %s, %s)
                """, [
                    f"Intervention prévue pour l’incident #{incident_id}",
                    incident_id,
                    'en_attente',
                    technicien_id,
                    state["duree"]
                ])

        except Exception as e:
            return Response({
                "response": f"❌ Erreur lors de la création de l'incident ou de l'intervention : {str(e)}"
            })

        # Réinitialisation
        user_states[user_id] = {
            "state": "initial",
            "description": "",
            "duree": 0,
            "technicien": ""
        }

        return Response({
            "response": "✅ Incident et intervention créés avec succès !",
            "created": True
        })

    return Response({
        "response": "Je n’ai pas compris. Essayez : Bonjour",
        "suggestions": [{"label": "Bonjour", "value": "Bonjour"}]
    })
