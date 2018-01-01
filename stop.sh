kill -9 `ps aux|grep wsgi| awk '{print $2}'`
