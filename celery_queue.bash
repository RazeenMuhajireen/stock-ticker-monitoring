#!/bin/bash
celery -A app.inventory.celery worker -Q normal --loglevel=debug