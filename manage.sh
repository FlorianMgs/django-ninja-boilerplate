#!/bin/bash

# Load environment variables from .env file and export them
set -a  # Automatically export all variables
source .env
set +a  # Turn off automatic export

# Run Django management commands in the web container
cd docker
docker compose -p ${PROJECT_NAME} exec web python manage.py "$@" 