# Installation

## Configuration

Edit smhi.py and set InfluxDB URL
Edit smhi.yaml and set Lat/Long and TEST to test or prod

If TEST is set to *test* it will just print it to stdout, otherwise it will post it to the InfluxDB database

## Standalone Docker container

```
./create.sh
kubectl apply -f smhi.yaml
```

## Kubernetes ArgoCD deployment

```
./create.sh
kubectl apply -f smhi.yaml
```
