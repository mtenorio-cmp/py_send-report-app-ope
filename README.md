docker-compose build --no-cache app
docker-compose up -d

git clone --branch main --depth 1 https://github.com/mtenorio-cmp/py_send-report-app-ope.git

/www/server/python_manager/versions/3.12.0/bin/gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8082 main:app

ps aux | grep python

elimina procesos por id
kill 3012267

para jecutar las pruebas test 

 
o python -m pytest tests/ -v