#!/bin/bash

if [[ -z $(docker ps | grep mongo) ]]; then 
    echo "You need to have the MongoDB docker container running before you can run the web server"; 
    exit 1
fi

docker build -t flask_web_server .
docker rm -f flask_web_server
docker run --name flask_web_server -t -p 127.0.0.1:5000:5000 --link mongo -it flask_web_server
