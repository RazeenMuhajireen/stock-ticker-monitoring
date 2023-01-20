#!/bin/bash
source /path/to/python/env/bin/activate
export FLASK_APP=run.py
flask db init
flask db migrate -m "Initial migration."
flask db upgrade