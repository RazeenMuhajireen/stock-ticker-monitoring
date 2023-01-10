#!/bin/bash
source /home/raz/myproject/env-stock/bin/activate
export FLASK_APP=run.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port 5000