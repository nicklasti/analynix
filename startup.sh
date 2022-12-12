echo "ok, were in the entrypoint"
python manage.py crontab add
echo "added the crontabs"
python manage.py crontab show
echo "showed the"