#!/bin/sh

docker build -t registry.cube.local:5000/smhi:2.2 .
#docker tag smhi:latest registry.cube.local:5000/smhi
docker push registry.cube.local:5000/smhi:2.2

#kubectl apply -f smhi.yaml

