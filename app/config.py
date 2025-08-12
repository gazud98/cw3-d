
import os
class Config:
    SECRET_KEY = "clave-secreta"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:proyectosgc2025@localhost/sgc"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Usa True solo si usas HTTPS


# Configuración de correo para Outlook / Microsoft 365