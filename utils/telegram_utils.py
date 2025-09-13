import requests
from config import settings

def send_message_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}
    response = requests.post(url, data=data)
    return response.json()

def send_image_to_telegram(image_path: str, caption: str = ""):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as img:
        files = {"photo": img}
        data = {"chat_id": settings.TELEGRAM_CHAT_ID, "caption": caption}
        response = requests.post(url, files=files, data=data)
    return response.json()

# Nueva función para enviar mensaje de texto a un usuario por su chat_id
def send_message_to_user(user_chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": user_chat_id, "text": text}
    response = requests.post(url, data=data)
    return response.json()