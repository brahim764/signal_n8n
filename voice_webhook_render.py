from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice_webhook():
    transcription = request.form.get("SpeechResult") or request.form.get("transcription") 
    caller = request.form.get("From")

    if not transcription or not caller:
        return Response('<?xml version="1.0"?><Response><Say language="fr-FR">Désolé, une erreur est survenue.</Say></Response>',
                        mimetype='application/xml')

    try:
        response = requests.post("https://tafraout.app.n8n.cloud/webhook/webhook-rdv",
                                 json={"transcription": transcription, "from": caller},
                                 timeout=10)
        data = response.json()
        phrase = data.get("reponse_vocale")
        if not phrase:
            raise ValueError("reponse_vocale manquant")
    except Exception:
        return Response('<?xml version="1.0"?><Response><Say language="fr-FR">Désolé, une erreur est survenue.</Say></Response>',
                        mimetype='application/xml')

    xml = f'<?xml version="1.0"?><Response><Say voice="woman" language="fr-FR">{phrase}</Say></Response>'
    return Response(xml, mimetype='application/xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
