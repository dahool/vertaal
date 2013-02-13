from django.db.models.signals import post_save, post_delete
from auditor import engine
import types
from django.db.models.loading import get_model

AUDIT_SESSION_ID = 'AUDIT_SESSION_ID'

def audit_model(m):
    if isinstance(m, types.StringTypes):
        model = get_model(m.split('.')[0],m.split('.')[1])
    else:
        model = m
    post_save.connect(engine.auditor_save_callback, sender=model)
    post_delete.connect(engine.auditor_delete_callback, sender=model)