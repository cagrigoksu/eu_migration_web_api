from datetime import datetime, timedelta
from firebase_admin import auth, firestore
from db.firebase_config import get_firestore_client
import uuid

db = get_firestore_client()

class AuthService:
    @staticmethod
    def create_user(email, password):
        try:
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=False
            )
            
            db.collection('users').document(user.uid).set({
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'api_key': None,
                'api_key_expiry': None
            })
            
            link = auth.generate_email_verification_link(email)
            return {'uid': user.uid, 'verification_link': link}
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    @staticmethod
    def verify_email(uid):
        try:
            auth.update_user(uid, email_verified=True)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def generate_api_key(uid):
        try:
            user_doc_ref = db.collection('users').document(uid)
            user_doc = user_doc_ref.get()
            
            if not user_doc.exists:
                user = auth.get_user(uid)
                user_doc_ref.set({
                    'email': user.email,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'api_key': None,
                    'api_key_expiry': None
                })
                user_doc = user_doc_ref.get()
            
            user_data = user_doc.to_dict()
            
            if user_data.get('api_key') and user_data.get('api_key_expiry'):
                expiry = user_data['api_key_expiry']
                if expiry > datetime.now():
                    raise Exception("User already has an active API key")
            
            api_key = str(uuid.uuid4())
            expiry_date = datetime.now() + timedelta(days=30)
            
            user_doc_ref.update({
                'api_key': api_key,
                'api_key_expiry': expiry_date
            })
            
            db.collection('api_keys').document(api_key).set({
                'user_id': uid,
                'created_at': firestore.SERVER_TIMESTAMP,
                'expires_at': expiry_date
            })
            
            return {'api_key': api_key, 'expires_at': expiry_date.isoformat()}
        except Exception as e:
            raise Exception(f"Error generating API key: {str(e)}")
    
    @staticmethod
    def validate_api_key(api_key):
        try:
            key_doc = db.collection('api_keys').document(api_key).get()
            if not key_doc.exists:
                return False
            
            key_data = key_doc.to_dict()
            expiry = key_data.get('expires_at')
            
            if expiry and expiry < datetime.now():
                db.collection('api_keys').document(api_key).delete()
                db.collection('users').document(key_data['user_id']).update({
                    'api_key': None,
                    'api_key_expiry': None
                })
                return False
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def get_user_profile(uid):
        try:
            user_doc_ref = db.collection('users').document(uid)
            user_doc = user_doc_ref.get()
            
            if not user_doc.exists:
                user = auth.get_user(uid)
                user_doc_ref.set({
                    'email': user.email,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'api_key': None,
                    'api_key_expiry': None
                })
                user_doc = user_doc_ref.get()
            
            return user_doc.to_dict()
        except Exception as e:
            return None