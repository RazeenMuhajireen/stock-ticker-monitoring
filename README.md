# stock-ticker-monitoring
Important Note:
please use a gmail account with app password created. Create an app password for the project and add account details
along with app password to .env

In order to deploy the project, following are required 
a. mysql:latest
b. redis 

To run:
1. create .env variable with respective server/password details.
2. in SQL create database stock_ticker
3. create python 3.9 environment
4. pip install -r requirements.txt 
5. change python3.9 env path in db_init.bash, celery_beat.bash, celery_queue_low.bash, celery_queue_normal.bash, start_debug.bash
6. run ./db_init.bash to create tables in sql 
7. run ./celery_beat.bash 
8. run ./celery_queue_low.bash
9. run ./celery_queue_normal.bash 
10. run ./start_debug.bash

Check postman documentation for API info. 

