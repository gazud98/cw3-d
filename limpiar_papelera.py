from app.extensions import db
from app.models.documento_model import DocumentoPapelera
import os
from datetime import datetime, timedelta
from app import create_app

app = create_app()

with app.app_context():
    limite = datetime.now() - timedelta(days=30)
    eliminados = DocumentoPapelera.query.filter(DocumentoPapelera.fecha_eliminado < limite).all()

    for doc in eliminados:
        try:
            if os.path.exists(doc.ruta_archivo):
                os.remove(doc.ruta_archivo)
        except Exception:
            pass
        db.session.delete(doc)

    db.session.commit()
