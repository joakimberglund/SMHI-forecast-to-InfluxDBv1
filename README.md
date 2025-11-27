# SMHI

Docker container that gets the SMHI forecast base on lat/long and posts it to an InfluxDB v1 database.

The container is design for running in a kubernetes cluster.

# Installation

## Configuration

Edit smhi.py and set InfluxDB URL
Edit smhi.yaml and set Lat/Long and TEST to test or prod

If TEST is set to *test* it will just print it to stdout, otherwise it will post it to the InfluxDB database

## Build the docker container
I use a local docker registry at registry.cube.local:5000
```
./build.sh
```

## Standalone Docker container
```
docker start smhi:2.2 ........ needs env vars...
```

## Kubernetes ArgoCD deployment
Load the ArgoCD app definition
```
kubectl apply -f smhi-argocd.yaml
```
