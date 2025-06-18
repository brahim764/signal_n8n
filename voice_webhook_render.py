import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# URL du webhook n8n pour envoyer les données
WEBHOOK_URL = "https://tafraout.app.n8n.cloud/webhook/webhook-rdv"

@app.route("/voice", methods=["GET", "POST"])
def voice_webhook():
    try:
        # Récupérer la transcription du message vocal et le numéro de téléphone de l'appelant
        transcription = request.values.get("TranscriptionText") or request.values.get("SpeechResult")
        phone_number = request.values.get("From")
        if not transcription or not phone_number:
            # Si l'un des champs requis est manquant, on lève une exception pour gérer l'erreur
            raise ValueError("Transcription ou numéro de téléphone manquant dans les données de la requête.")
        
        # Préparer les données à envoyer au webhook n8n
        payload = {
            "transcription": transcription,
            "number": phone_number
        }
        
        # Envoyer la requête POST au webhook n8n avec les données JSON
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()  # lever une exception si code HTTP != 200
        
        # Analyser la réponse JSON reçue du webhook n8n
        data = response.json()
        reponse_vocale = data.get("reponse_vocale")
        if not reponse_vocale:
            raise ValueError("La réponse vocale n'a pas été trouvée dans la réponse du webhook.")
        
        # Construire la réponse XML (LaML) à renvoyer à SignalWire
        # On utilise <Say> pour lire la réponse vocale renvoyée par n8n.
        # On définit la langue en français pour une meilleure synthèse vocale.
        # Échapper les caractères spéciaux XML dans la réponse vocale
        reponse_vocale_text = reponse_vocale.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        xml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Say language="fr-FR" voice="alice">{reponse_vocale_text}</Say></Response>'
        
        # Retourner la réponse XML avec le bon content-type
        return Response(xml_response, content_type="text/xml; charset=utf-8")
    except Exception as e:
        # En cas d'erreur, consigner l'erreur dans les logs puis renvoyer un message d'erreur vocal en XML
        print(f"Erreur dans le webhook vocal : {e}", flush=True)
        error_message = "Désolé, une erreur s'est produite. Veuillez réessayer plus tard."
        error_xml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Say language="fr-FR" voice="alice">{error_message}</Say></Response>'
        return Response(error_xml, content_type="text/xml; charset=utf-8")

# Démarrage de l'application Flask (pour exécution locale)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
