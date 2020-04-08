#!/usr/bin/env bash

docker stop wiremock; docker rm wiremock; docker run --name wiremock -p 8080:8080 -v $PWD/test/stubs:/home/wiremock rodolpheche/wiremock --verbose