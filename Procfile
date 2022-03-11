% prepara el repositorio para su despliegue. 
release: sh -c 'cd MakeAMate && python manage.py migrate'
% especifica el comando para lanzar Decide
web: sh -c 'cd MakeAMate && gunicorn MakeAMate.wsgi --log-file -'
