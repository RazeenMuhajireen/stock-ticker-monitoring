# stock-ticker-monitoring

use a gmail account with app password created. Create an app password for the project 
To run:
1. create .env variable with respective server/password details.
2. in SQL create database stock_ticker
3. run ./db_init.bash to create tables in sql 
4. run ./celery_beat.bash 
5. run ./celery_queue_low.bash
6. run ./celery_queue_normal.bash 
7. run ./start_debug.bash

