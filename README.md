# proxy

## Выполнила Талмаза Виктория 

http/https proxy, repeater and dirbuster в рамках домашнего задания по курсу Безопасность интернет-приложений ([ссылка](https://docs.google.com/document/d/1QaQ-Nc_eE4dBKZwQbA4E2o8pOJ3CktgsKDAn375iY24/edit#)).

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


