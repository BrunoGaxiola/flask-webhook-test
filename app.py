from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "cX8H6N37n1u/yTO5xPeEf8bGNG+otUedsEqvxFzeyNc"

@app.route("/", methods=["GET", "POST", "HEAD"])
def webhook():

    # --- Verificación del webhook (Meta envía GET) ---
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Error: invalid token", 403

    # --- Webhooks recibidos (Meta envía POST) ---
    if request.method == "POST":
        data = request.get_json()
        print("\n🔥 Webhook recibido:")
        print(data)
        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    # Importante para Render.com
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)