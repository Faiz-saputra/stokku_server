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
@app.route("/check-stok")
def check_stok():
    try:
        ref = db.reference("barang")
        data = ref.get()

        # Kalau node barang belum ada
        if data is None:
            return jsonify({
                "status": "ok",
                "message": "node 'barang' belum ada di database"
            })

        for kode, item in data.items():
            # Aman walaupun field tidak lengkap
            stok = int(item.get("stok", 0))
            nama = item.get("nama", "Barang tanpa nama")

            if stok <= MIN_STOK:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title="⚠️ Stok Rendah",
                        body=f"{nama} tersisa {stok}"
                    ),
                    topic="allUser"
                )
                messaging.send(message)

        return jsonify({
            "status": "ok",
            "message": "stok berhasil dicek"
        })

    except Exception as e:
        # Ini PENTING supaya error terlihat
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/")
def home():
    return "Flask server berjalan!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)



