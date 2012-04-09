#!/bin/bash
git pull
echo "Applying update ... (this could take some time)"
python manage.py syncdb --noinput
python manage.py appupdate
python manage.py collectstatic --noinput
python manage.py compilemessages
echo "Reload"
touch ../apache/django.wsgi
echo ""
echo "Finished"
echo ""