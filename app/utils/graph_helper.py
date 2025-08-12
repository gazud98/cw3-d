import requests
import base64
from app.config import (
    GRAPH_CLIENT_ID,
    GRAPH_CLIENT_SECRET,
    GRAPH_SCOPE,
    GRAPH_TOKEN_URL
)

def obtener_token_accesso():
    data = {
        "client_id": GRAPH_CLIENT_ID,
        "client_secret": GRAPH_CLIENT_SECRET,
        "scope": GRAPH_SCOPE,
        "grant_type": "client_credentials"
    }

    response = requests.post(GRAPH_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def enviar_correo_graph(destinatario, asunto, cuerpo_texto, nombre_archivo=None, contenido_archivo=None):
    token = obtener_token_accesso()
    url = "https://graph.microsoft.com/v1.0/users/desarrollo@pasteurlab.com/sendMail"

    mensaje = {
        "message": {
            "subject": asunto,
            "body": {
                "contentType": "Text",
                "content": cuerpo_texto
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": destinatario
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

 
    if nombre_archivo and contenido_archivo:
        contenido_base64 = base64.b64encode(contenido_archivo).decode('utf-8')
        mensaje["message"]["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": nombre_archivo,
                "contentBytes": contenido_base64,
                "contentType": "application/octet-stream"
            }
        ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=mensaje)

    if response.status_code != 202:
        print(response.text)  # Ayuda en debugging
    return response.status_code == 202
