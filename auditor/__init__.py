from django.db.models.signals import post_save, post_delete
from auditor import engine

AUDIT_SESSION_ID = 'AUDIT_SESSION_ID'

def audit_model(m):
    post_save.connect(engine.auditor_save_callback, sender=m)
    post_delete.connect(engine.auditor_delete_callback, sender=m)