#!/bin/bash

nohup python manage.py runserver 0.0.0.0:8000 >log &

exit 
uwsgi -s 127.0.0.1:7000 --module wsgi --chdir /data/web/yunwei --pythonpath /data/web/yunwei --enable-threads -M -p4

pgrep -fl manage || \
cd webssh/ && python manage.py runserver 0.0.0.0:8001 

#pgrep -fl webshell.py || python WebShell-0.9.6/webshell.py -c "ssh  -o StrictHostKeyChecking=no -p22 localhost" --ssl-disable &



