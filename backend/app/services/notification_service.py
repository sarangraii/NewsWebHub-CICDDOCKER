# import firebase_admin
# from firebase_admin import credentials, messaging
# from app.config import settings
# from pathlib import Path
# import os

# class NotificationService:
#     def __init__(self):
#         self.initialized = False
#         self.setup_firebase()
    
#     def setup_firebase(self):
#         """Initialize Firebase Admin SDK"""
#         try:
#             cred_path = Path(os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json"))
            
#             if not cred_path.exists():
#                 print("⚠️ Firebase credentials not found - notifications disabled")
#                 return
            
#             if not firebase_admin._apps:
#                 cred = credentials.Certificate(str(cred_path))
#                 firebase_admin.initialize_app(cred)
#                 self.initialized = True
#                 print("✅ Firebase initialized for notifications")
#             else:
#                 self.initialized = True
#         except Exception as e:
#             print(f"❌ Firebase setup error: {e}")
    
#     async def send_breaking_news(self, article: dict):
#         """Send breaking news notification to all users"""
#         if not self.initialized:
#             return
        
#         try:
#             title = article.get("title", "Breaking News")[:100]
#             body = article.get("description", "")[:200]
#             article_id = str(article.get("_id", ""))
            
#             message = messaging.Message(
#                 notification=messaging.Notification(
#                     title=f"🚨 Breaking: {title}",
#                     body=body,
#                 ),
#                 data={
#                     "articleId": article_id,
#                     "type": "breaking",
#                     "url": f"/article/{article_id}"
#                 },
#                 topic="breaking_news"  # All users subscribed to this topic
#             )
            
#             response = messaging.send(message)
#             print(f"✅ Breaking news sent: {response}")
#             return response
            
#         except Exception as e:
#             print(f"❌ Notification error: {e}")
#             return None
    
#     async def send_topic_notification(self, article: dict, topic: str):
#         """Send notification for specific topic (Sports, Tech, etc.)"""
#         if not self.initialized:
#             return
        
#         try:
#             title = article.get("title", "")[:100]
#             body = article.get("description", "")[:200]
#             article_id = str(article.get("_id", ""))
            
#             # Topic names must match Firebase format: letters, numbers, and underscores only
#             safe_topic = topic.lower().replace(" ", "_").replace("-", "_")
            
#             message = messaging.Message(
#                 notification=messaging.Notification(
#                     title=f"{topic}: {title}",
#                     body=body,
#                 ),
#                 data={
#                     "articleId": article_id,
#                     "type": "topic",
#                     "topic": topic,
#                     "url": f"/article/{article_id}"
#                 },
#                 topic=safe_topic
#             )
            
#             response = messaging.send(message)
#             print(f"✅ Topic notification sent ({topic}): {response}")
#             return response
            
#         except Exception as e:
#             print(f"❌ Topic notification error: {e}")
#             return None

# notification_service = NotificationService()

import firebase_admin
from firebase_admin import credentials, messaging
from pathlib import Path
import os
import json
import traceback

class NotificationService:
    def __init__(self):
        self.initialized = False
        self.setup_firebase()
    
    def setup_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Method 1: Try JSON from environment variable first
            cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            
            if cred_json:
                print("🔍 Found FIREBASE_CREDENTIALS_JSON environment variable")
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            else:
                # Method 2: Try Render's secret file path
                cred_path = Path("/etc/secrets/firebase-credentials.json")
                
                print(f"🔍 Looking for credentials at: {cred_path}")
                print(f"🔍 File exists: {cred_path.exists()}")
                
                # Debug: List all files in /etc/secrets/
                secrets_dir = Path("/etc/secrets")
                if secrets_dir.exists():
                    try:
                        files = list(secrets_dir.iterdir())
                        print(f"🔍 Files in /etc/secrets/: {files}")
                    except Exception as e:
                        print(f"🔍 Could not list /etc/secrets/: {e}")
                
                if not cred_path.exists():
                    # Method 3: Try local path as fallback (for local development)
                    local_path = Path("firebase-credentials.json")
                    if local_path.exists():
                        print(f"🔍 Using local credentials at: {local_path}")
                        cred_path = local_path
                    else:
                        print("⚠️ Firebase credentials not found - notifications disabled")
                        print("💡 Add firebase-credentials.json as a Secret File in Render")
                        print("💡 Or set FIREBASE_CREDENTIALS_JSON environment variable")
                        return
                
                if cred_path.exists():
                    print(f"🔍 File size: {cred_path.stat().st_size} bytes")
                
                cred = credentials.Certificate(str(cred_path))
            
            # Initialize Firebase if not already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
                self.initialized = True
                print("✅ Firebase initialized for notifications")
            else:
                self.initialized = True
                print("✅ Firebase already initialized")
                
        except json.JSONDecodeError as e:
            print(f"❌ Firebase JSON parsing error: {e}")
            print("💡 Check if FIREBASE_CREDENTIALS_JSON is valid JSON")
            traceback.print_exc()
        except Exception as e:
            print(f"❌ Firebase setup error: {e}")
            traceback.print_exc()
    
    async def send_breaking_news(self, article: dict):
        """Send breaking news notification to all users"""
        if not self.initialized:
            print("⚠️ Cannot send notification - Firebase not initialized")
            return
        
        try:
            title = article.get("title", "Breaking News")[:100]
            body = article.get("description", "")[:200]
            article_id = str(article.get("_id", ""))
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"🚨 Breaking: {title}",
                    body=body,
                ),
                data={
                    "articleId": article_id,
                    "type": "breaking",
                    "url": f"/article/{article_id}"
                },
                topic="breaking_news"  # All users subscribed to this topic
            )
            
            response = messaging.send(message)
            print(f"✅ Breaking news sent: {response}")
            return response
            
        except Exception as e:
            print(f"❌ Notification error: {e}")
            traceback.print_exc()
            return None
    
    async def send_topic_notification(self, article: dict, topic: str):
        """Send notification for specific topic (Sports, Tech, etc.)"""
        if not self.initialized:
            print("⚠️ Cannot send notification - Firebase not initialized")
            return
        
        try:
            title = article.get("title", "")[:100]
            body = article.get("description", "")[:200]
            article_id = str(article.get("_id", ""))
            
            # Topic names must match Firebase format: letters, numbers, and underscores only
            safe_topic = topic.lower().replace(" ", "_").replace("-", "_")
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"{topic}: {title}",
                    body=body,
                ),
                data={
                    "articleId": article_id,
                    "type": "topic",
                    "topic": topic,
                    "url": f"/article/{article_id}"
                },
                topic=safe_topic
            )
            
            response = messaging.send(message)
            print(f"✅ Topic notification sent ({topic}): {response}")
            return response
            
        except Exception as e:
            print(f"❌ Topic notification error: {e}")
            traceback.print_exc()
            return None
    
    async def send_personalized_notification(self, article: dict, fcm_token: str):
        """Send notification to a specific device"""
        if not self.initialized:
            print("⚠️ Cannot send notification - Firebase not initialized")
            return
        
        try:
            title = article.get("title", "")[:100]
            body = article.get("description", "")[:200]
            article_id = str(article.get("_id", ""))
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={
                    "articleId": article_id,
                    "type": "personalized",
                    "url": f"/article/{article_id}"
                },
                token=fcm_token
            )
            
            response = messaging.send(message)
            print(f"✅ Personalized notification sent: {response}")
            return response
            
        except Exception as e:
            print(f"❌ Personalized notification error: {e}")
            traceback.print_exc()
            return None

# Singleton instance
notification_service = NotificationService()