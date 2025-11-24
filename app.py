from flask import Flask, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = "cX8H6N37n1u/yTO5xPeEf8bGNG+otUedsEqvxFzeyNc"
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": { "body": message }
    }

    response = requests.post(url, json=data, headers=headers)
    print("Send message response:", response.json())
    return response.json()

@app.route("/", methods=["GET", "POST", "HEAD"])
def webhook():

    # HEAD request Render health check
    if request.method == "HEAD":
        return "", 200

    # Verification GET
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid token", 403
    
    # Receive webhook POST
    if request.method == "POST":
        body = request.get_json()
        print("Webhook received:")
        print(body)

        try:
            entry = body["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            messages = value.get("messages")

            if messages:
                msg = messages[0]
                sender = msg["from"]

                msg_type = msg["type"]

                # --- TEXT MESSAGE ---
                if msg_type == "text":
                    user_text = msg["text"]["body"]
                    print(f"User wrote: {user_text}")
                    send_whatsapp_message(sender, "Gracias por tu mensaje de texto.")

                # --- INTERACTIVE BUTTON ---
                elif msg_type == "button":
                    button_payload = msg["button"]["payload"]
                    button_text = msg["button"]["text"]

                    print(f"User pressed button: {button_text} | Payload: {button_payload}")

                    # Respond based on the payload
                    if button_payload == "Si, confirmo la cita.":
                        send_whatsapp_message(sender, "Perfecto, tu cita ha sido confirmada. Nos vemos pronto.")
                    elif button_payload == "No, cancelo la cita.":
                        send_whatsapp_message(sender, "De acuerdo, tu cita ha sido cancelada.")
                    else:
                        send_whatsapp_message(sender, "Esa respuesta no es válida. Seleccione una opción válida.")
        except Exception as e:
            print("Error handling webhook:", e)

        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)