#!/bin/bash

if [[ -z $(docker ps | grep mongo) ]]; then 
    echo "You need to have the MongoDB docker container running before you can run the device api server"; 
    exit 1
fi

docker build -t flask_device_api .
docker rm -f flask_device_api
docker run --name flask_device_api -t -p 127.0.0.1:9999:9999 --link mongo -it flask_device_api
