import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class EmailManager:
    """Manages email operations"""
    
    def __init__(self, email_config: Dict[str, str] = None):
        self.config = email_config or {}
        self.smtp_server = None
        self.imap_server = None
    
    def setup_email(self, email_address: str, password: str, smtp_server: str = None, 
                   imap_server: str = None, smtp_port: int = 587, imap_port: int = 993):
        """Setup email configuration"""
        self.config = {
            'email': email_address,
            'password': password,
            'smtp_server': smtp_server or self._get_smtp_server(email_address),
            'imap_server': imap_server or self._get_imap_server(email_address),
            'smtp_port': smtp_port,
            'imap_port': imap_port
        }
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachments: List[str] = None, cc: List[str] = None) -> str:
        """Send an email"""
        try:
            if not self.config.get('email'):
                return "Email not configured. Please set up email credentials first."
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
                recipients = [to_email] + cc
            else:
                recipients = [to_email]
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email'], self.config['password'])
            text = msg.as_string()
            server.sendmail(self.config['email'], recipients, text)
            server.quit()
            
            return f"Email sent successfully to {to_email}"
        
        except Exception as e:
            return f"Failed to send email: {str(e)}"
    
    def read_emails(self, folder: str = 'INBOX', limit: int = 10, unread_only: bool = True) -> List[Dict[str, Any]]:
        """Read emails from specified folder"""
        try:
            if not self.config.get('email'):
                return [{"error": "Email not configured"}]
            
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            mail.login(self.config['email'], self.config['password'])
            mail.select(folder)
            
            # Search for emails
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, data = mail.search(None, search_criteria)
            
            if status != 'OK':
                return [{"error": "Failed to search emails"}]
            
            email_ids = data[0].split()
            emails = []
            
            # Get recent emails (limit)
            for email_id in email_ids[-limit:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    subject = email_message['Subject']
                    sender = email_message['From']
                    date = email_message['Date']
                    
                    # Get email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8')
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode('utf-8')
                    
                    emails.append({
                        'id': email_id.decode(),
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'body': body[:500] + "..." if len(body) > 500 else body
                    })
            
            mail.close()
            mail.logout()
            
            return list(reversed(emails))  # Most recent first
        
        except Exception as e:
            return [{"error": f"Failed to read emails: {str(e)}"}]
    
    def _get_smtp_server(self, email_address: str) -> str:
        """Get SMTP server based on email domain"""
        domain = email_address.split('@')[1].lower()
        smtp_servers = {
            'gmail.com': 'smtp.gmail.com',
            'outlook.com': 'smtp-mail.outlook.com',
            'hotmail.com': 'smtp-mail.outlook.com',
            'yahoo.com': 'smtp.mail.yahoo.com',
            'icloud.com': 'smtp.mail.me.com'
        }
        return smtp_servers.get(domain, 'smtp.gmail.com')
    
    def _get_imap_server(self, email_address: str) -> str:
        """Get IMAP server based on email domain"""
        domain = email_address.split('@')[1].lower()
        imap_servers = {
            'gmail.com': 'imap.gmail.com',
            'outlook.com': 'imap-mail.outlook.com',
            'hotmail.com': 'imap-mail.outlook.com',
            'yahoo.com': 'imap.mail.yahoo.com',
            'icloud.com': 'imap.mail.me.com'
        }
        return imap_servers.get(domain, 'imap.gmail.com')

class SlackManager:
    """Manages Slack integration"""
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
    
    def setup_slack(self, bot_token: str):
        """Setup Slack bot token"""
        self.bot_token = bot_token
    
    def send_message(self, channel: str, message: str, thread_ts: str = None) -> str:
        """Send a message to a Slack channel"""
        try:
            if not self.bot_token:
                return "Slack not configured. Please set bot token first."
            
            headers = {
                'Authorization': f'Bearer {self.bot_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'channel': channel,
                'text': message
            }
            
            if thread_ts:
                data['thread_ts'] = thread_ts
            
            response = requests.post(
                f"{self.base_url}/chat.postMessage",
                headers=headers,
                json=data
            )
            
            result = response.json()
            
            if result.get('ok'):
                return f"Message sent to {channel}"
            else:
                return f"Failed to send message: {result.get('error', 'Unknown error')}"
        
        except Exception as e:
            return f"Failed to send Slack message: {str(e)}"
    
    def get_channels(self) -> List[Dict[str, str]]:
        """Get list of Slack channels"""
        try:
            if not self.bot_token:
                return [{"error": "Slack not configured"}]
            
            headers = {
                'Authorization': f'Bearer {self.bot_token}'
            }
            
            response = requests.get(
                f"{self.base_url}/conversations.list",
                headers=headers
            )
            
            result = response.json()
            
            if result.get('ok'):
                channels = []
                for channel in result.get('channels', []):
                    channels.append({
                        'id': channel['id'],
                        'name': channel['name'],
                        'is_private': channel.get('is_private', False)
                    })
                return channels
            else:
                return [{"error": result.get('error', 'Unknown error')}]
        
        except Exception as e:
            return [{"error": f"Failed to get channels: {str(e)}"}]
    
    def get_messages(self, channel: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from a channel"""
        try:
            if not self.bot_token:
                return [{"error": "Slack not configured"}]
            
            headers = {
                'Authorization': f'Bearer {self.bot_token}'
            }
            
            params = {
                'channel': channel,
                'limit': limit
            }
            
            response = requests.get(
                f"{self.base_url}/conversations.history",
                headers=headers,
                params=params
            )
            
            result = response.json()
            
            if result.get('ok'):
                messages = []
                for message in result.get('messages', []):
                    messages.append({
                        'text': message.get('text', ''),
                        'user': message.get('user', ''),
                        'timestamp': message.get('ts', ''),
                        'type': message.get('type', '')
                    })
                return messages
            else:
                return [{"error": result.get('error', 'Unknown error')}]
        
        except Exception as e:
            return [{"error": f"Failed to get messages: {str(e)}"}]

class TranslationManager:
    """Manages translation services"""
    
    def __init__(self, api_key: str = None, service: str = "google"):
        self.api_key = api_key
        self.service = service
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> str:
        """Translate text to target language"""
        try:
            if self.service == "google" and self.api_key:
                return self._google_translate(text, target_language, source_language)
            else:
                # Fallback to a simple mock translation
                return self._mock_translate(text, target_language)
        
        except Exception as e:
            return f"Translation failed: {str(e)}"
    
    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        try:
            if self.service == "google" and self.api_key:
                return self._google_detect_language(text)
            else:
                return "Language detection not available"
        
        except Exception as e:
            return f"Language detection failed: {str(e)}"
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        # Common language codes
        return [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"}
        ]
    
    def _google_translate(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Use Google Translate API"""
        try:
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': self.api_key,
                'q': text,
                'target': target_lang,
                'source': source_lang if source_lang != 'auto' else None
            }
            
            response = requests.post(url, params=params)
            result = response.json()
            
            if 'data' in result:
                return result['data']['translations'][0]['translatedText']
            else:
                return f"Translation error: {result.get('error', {}).get('message', 'Unknown error')}"
        
        except Exception as e:
            return f"Google Translate error: {str(e)}"
    
    def _google_detect_language(self, text: str) -> str:
        """Use Google Translate API for language detection"""
        try:
            url = "https://translation.googleapis.com/language/translate/v2/detect"
            params = {
                'key': self.api_key,
                'q': text
            }
            
            response = requests.post(url, params=params)
            result = response.json()
            
            if 'data' in result:
                detection = result['data']['detections'][0][0]
                return f"Detected language: {detection['language']} (confidence: {detection['confidence']:.2f})"
            else:
                return f"Detection error: {result.get('error', {}).get('message', 'Unknown error')}"
        
        except Exception as e:
            return f"Language detection error: {str(e)}"
    
    def _mock_translate(self, text: str, target_lang: str) -> str:
        """Mock translation for demonstration"""
        mock_translations = {
            'es': f"[ES] {text}",
            'fr': f"[FR] {text}",
            'de': f"[DE] {text}",
            'it': f"[IT] {text}",
            'pt': f"[PT] {text}",
            'ru': f"[RU] {text}",
            'ja': f"[JA] {text}",
            'ko': f"[KO] {text}",
            'zh': f"[ZH] {text}",
            'ar': f"[AR] {text}",
            'hi': f"[HI] {text}"
        }
        
        return mock_translations.get(target_lang, f"[{target_lang.upper()}] {text}")

# Communication hub that combines all services
class CommunicationHub:
    """Central hub for all communication services"""
    
    def __init__(self):
        self.email_manager = EmailManager()
        self.slack_manager = SlackManager()
        self.translation_manager = TranslationManager()
    
    def setup_email(self, email: str, password: str, smtp_server: str = None, imap_server: str = None):
        """Setup email configuration"""
        self.email_manager.setup_email(email, password, smtp_server, imap_server)
    
    def setup_slack(self, bot_token: str):
        """Setup Slack configuration"""
        self.slack_manager.setup_slack(bot_token)
    
    def setup_translation(self, api_key: str, service: str = "google"):
        """Setup translation service"""
        self.translation_manager = TranslationManager(api_key, service)
    
    def send_communication(self, service: str, **kwargs) -> str:
        """Send communication via specified service"""
        if service == "email":
            return self.email_manager.send_email(**kwargs)
        elif service == "slack":
            return self.slack_manager.send_message(**kwargs)
        else:
            return f"Unknown communication service: {service}"
    
    def translate_message(self, text: str, target_language: str) -> str:
        """Translate a message"""
        return self.translation_manager.translate_text(text, target_language)