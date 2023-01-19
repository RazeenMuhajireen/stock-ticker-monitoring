# stock-ticker-monitoring
Important Note:
please use a gmail account with app password created. Create an app password for the project and add account details
along with app password to .env

To run:
1. create .env variable with respective server/password details.
2. in SQL create database stock_ticker
3. pip install -r requirements.txt 
4. run ./db_init.bash to create tables in sql 
5. run ./celery_beat.bash 
6. run ./celery_queue_low.bash
7. run ./celery_queue_normal.bash 
8. run ./start_debug.bash

