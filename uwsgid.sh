#!/bin/sh 
# chkconfig: - 99 20 
# description: uwsgi Service Control Script 
# //如需使用 chkconfig 管理，注意以上两行内容不可少 

Uwsgi='/usr/bin/uwsgi'
case "$1" in 
    start) 
      echo "start uwsgi..."
	   #$Uwsgi --http 0.0.0.0:8000 --module wsgi  --chdir ./ --pythonpath .. --enable-threads -M -p4  --reload-mercy 4  --worker-reload-mercy 4 --http-timeout 1000
	   uwsgi -s 127.0.0.1:7000 --module wsgi --chdir /data/web/yunwei --pythonpath /data/web/yunwei --enable-threads -M -p4 
	   sleep 1
	   ps -elf | grep -v grep | grep uwsgi >>/dev/null && echo 'start uwsgi ok!'
        ;; 
    stop) 
	  echo "stop uwsgi..."
	  killall -9 uwsgi
      [ -f /tmp/uwsgi.pid ] && rm -rf /tmp/uwsgi.pid
	  sleep 1
	  pgrep /bin/uwsgi || echo 'stop uwsgi ok!'
        ;; 
    restart) 
        $0 stop 
        $0 start 
        ;; 
    reload) 
		echo "uwsgi reload..."
	#残酷
        #[ -f /tmp/uwsgi.pid ] && kill -TERM `cat /tmp/uwsgi.pid` 
        [ -f /tmp/uwsgi.pid ] && kill -HUP `cat /tmp/uwsgi.pid` 
		echo "uwsgi reload ok!"
        ;; 
	status)
		ps aux | grep uwsgi | grep -v grep | grep -v status
		;;
    *) 
                echo "Usage: $0 {start|stop|restart|reload}" 
                exit 1 
esac 
exit 0 
