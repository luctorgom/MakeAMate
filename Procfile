% prepara el repositorio para su despliegue. 
release: sh -c 'cd MakeAMate && python manage.py makemigrations && python manage.py migrate && python manage.py makemigrations && python manage.py migrate'
% especifica el comando para lanzar MakeAMate
web: sh -c 'cd MakeAMate && daphne -b 0.0.0.0 -p $PORT MakeAMate.asgi:application'
