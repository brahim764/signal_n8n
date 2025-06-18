from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/webhook-voice", methods=["POST"])
def signalwire_voice():
    transcription = request.form.get("SpeechResult", "") or request.form.get("transcription", "")
    caller = request.form.get("From", "")

    n8n_webhook_url = "https://tafroute.app.n8n.cloud/webhook/appel"
    try:
        n8n_response = requests.post(n8n_webhook_url, json={
            "transcription": transcription,
            "from": caller
        }, timeout=10)
        n8n_response.raise_for_status()
        data = n8n_response.json()
    except Exception as e:
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response><Say language="fr-FR">Désolé, une erreur est survenue.</Say></Response>', status=200, mimetype='application/xml')

    phrase = data.get("reponse_vocale", "Désolé, je n'ai pas compris. Veuillez réessayer.")
    xml_response = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say voice=\"woman\" language=\"fr-FR\">" + phrase + "</Say></Response>"
    return Response(xml_response, status=200, mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
