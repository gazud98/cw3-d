
import os
class Config:
    SECRET_KEY = "clave-secreta"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:proyectosgc2025@localhost/sgc"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Usa True solo si usas HTTPS


# Configuración de correo para Outlook / Microsoft 365


GRAPH_CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID", "6cc6a660-b350-48aa-acee-6fdbd9d9d31b")
GRAPH_CLIENT_SECRET = os.environ.get("GRAPH_CLIENT_SECRET", "sEr8Q~5ucR7m-asV3aKRV6DrSHpWOxwk25kIBcgH")
GRAPH_TENANT_ID = os.environ.get("GRAPH_TENANT_ID", "c7df72f7-4df0-418b-80f8-e75d99e29ad8")
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_TOKEN_URL = (
    f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"
)
