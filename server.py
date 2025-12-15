import json
import os
from flask import Flask, jsonify
import firebase_admin 
from firebase_admin import credentials, db, messaging

app = Flask(__name__)

# 1. Firebase Admin SDK
firebase_key = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])

cred = credentials.Certificate(firebase_key)

firebase_admin.initialize_app(cred, {
    "databaseURL": os.environ["FIREBASE_DB_URL"]
})

MINIMUM_STOK = 5

def send_fcm(title, body, topic="allUser"):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic=topic
    )
    messaging.send(message)
    print("[FCM SENDED]", title, body)

@app.route("/check-stok")
def check_stok():
    ref = db.reference("barang")
    data = ref.get()

    if not data:
        return jsonify({"message": "no data"})

    for kode, item in data.items():
        nama = item.get("nama", "Barang")
        stok = item.get("stok", 0)
        min_stok = item.get("min_stok", MINIMUM_STOK)

        if stok <= min_stok:
            send_fcm(
                title="⚠️ Stok Rendah!",
                body=f"{nama} tersisa {stok} item!"
            )

    return jsonify({"message": "stok checked"})

@app.route("/")
def home():
    return "Flask server berjalan!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


