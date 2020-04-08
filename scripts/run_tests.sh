#!/usr/bin/env bash

docker stop wiremock; docker rm wiremock; docker run -d --name wiremock -p 8080:8080 -v $PWD/test/stubs:/home/wiremock rodolpheche/wiremock --verbose
echo "started wiremock on the background"

sleep 5

export PYTHONPATH=`pwd`
pytest -vv --cov=crawlerFromMars --cov-fail-under=90 test/

echo "tests run successfully - will stop and remove wiremock"
docker stop wiremock; docker rm wiremock