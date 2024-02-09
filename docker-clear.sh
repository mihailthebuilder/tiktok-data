#!/bin/bash

docker rmi -f $(docker images -aq)
docker rm -v -f $(docker ps -qa)
