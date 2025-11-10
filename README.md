# Installation

## Configuration

Edit smhi.py and set InfluxDB URL
Edit smhi.yaml and set Lat/Long and TEST to test or prod

If TEST is set to *test* it will just print it to stdout, otherwise it will post it to the InfluxDB database

## Build the docker container
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
