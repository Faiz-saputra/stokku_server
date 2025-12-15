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

MIN_STOK = 5

def send_fcm(title, body, topic="allUser"):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic=topic
    )
    messaging.send(message)
    print("[FCM SENDED]", title, body)

@app.route("/check-stok")
def check_stok():
    try:
        ref = db.reference("inventory")
        data = ref.get()

        if not data:
            return jsonify({"message": "Tidak ada data inventory", "status": "ok"})

        for user_id, items in data.items():
            for item_id, item in items.items():
                stok = item.get("stok", 0)
                nama = item.get("nama", "Barang tanpa nama")

                if stok <= MIN_STOK:
                    send_notification(
                        title="⚠️ Stok Rendah",
                        body=f"{nama} tersisa {stok}"
                    )

        return jsonify({"message": "stok berhasil dicek", "status": "ok"})

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"})



@app.route("/")
def home():
    return "Flask server berjalan!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)






