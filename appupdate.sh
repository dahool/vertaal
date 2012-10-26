#!/bin/bash
echo "Applying update ... (this could take some time)"
sleep 2
python -mcompileall . &>/dev/null
python manage.py syncdb --noinput
python manage.py appupdate
#python manage.py collectstatic --noinput
python manage.py evolve --execute --noinput
python manage.py compilemessages
echo "Reload"
touch wsgi.py
echo ""
echo "Finished"
echo ""
