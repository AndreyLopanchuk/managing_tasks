#!/bin/bash

docker-compose down #-v

docker-compose up --build -d

sleep 1

docker ps -a

docker-compose logs -f


# сделать скрипт исполняемым chmod +x rebuild.sh
# запуск скрипта ./rebuild.sh

#black .
#isort --profile black .
#flake8 .
#mypy --ignore-missing-imports .