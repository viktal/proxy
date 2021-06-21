# proxy

**Функционал**  
proxy - проксирование http и https запросов с сохранением в базу sqlite для последующего просмотра   
repeater - повтор проксированных запросов из базы  
dirbuster - сканер уязвимости. В url запроса подставляются [слова из списка](https://github.com/maurosoria/dirsearch/blob/master/db/dicc.txt) и проверяется код ответа    

Run Dockerfile:  
```
docker build -t proxy . && docker run -p 8000:8000 -p 8080:8080 proxy
```
Proxy работает на 0.0.0.1:8080  
Web_interface работает на 0.0.0.1:8000 (можно запустить в браузере) 
* /requests – список запросов
* /request/id – вывод 1 запроса
* /repeat/id – повторная отправка запроса
* /scan/id – сканирование запроса (Dirbuster - выполняется довольно долго)


