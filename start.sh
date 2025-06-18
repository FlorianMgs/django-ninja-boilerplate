#!/bin/bash

# Load environment variables from .env file and export them
set -a  # Automatically export all variables
source .env
set +a  # Turn off automatic export

cd docker
docker compose up --build "$@" 