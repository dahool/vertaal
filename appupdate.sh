#!/bin/bash
echo "Applying update ... (this could take some time)"
python -mcompileall
python manage.py syncdb --noinput
python manage.py appupdate
python manage.py collectstatic --noinput
python manage.py compilemessages
echo "Reload"
touch ../apache/django.wsgi
echo ""
echo "Finished"
echo ""