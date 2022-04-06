% prepara el repositorio para su despliegue. 
release: sh -c 'cd MakeAMate && python manage.py makemigrations && python manage.py migrate'
% especifica el comando para lanzar MakeAMate
web: sh -c 'cd MakeAMate && gunicorn MakeAMate.wsgi --log-file -'
