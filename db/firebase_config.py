import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json'))
firebase_admin.initialize_app(cred)

db = firestore.client()

def get_firestore_client():
    return db

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None