#!/bin/sh

cd Docker
docker build -t registry.cube.local:5000/smhi:3.0 .
docker push registry.cube.local:5000/smhi:3.0
cd ..

# 1.0   Initial
# 2.0   Envvars
# 2.1   Bugfix
# 2.2   Bugfix
# 3.0	Switch to snow1g API

