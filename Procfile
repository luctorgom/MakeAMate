% especifica el comando para lanzar MakeAMate
release: sh -c 'cd MakeAMate && python manage.py collectstatic'
web: sh -c 'cd MakeAMate && gunicorn MakeAMate.wsgi --log-file -'
