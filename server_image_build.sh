#!/usr/bin/env bash
docker container stop report_server
docker container rm report_server
docker image rm qq_server:0.0.1
docker image build -t qq_server:0.0.1 .
# 输出日志
#docker container run --name=report_server --network qq_robot --ip 172.20.0.9 -v $(pwd)/server_log:/usr/src/app/log -p 44551:44551 qq_server:0.0.2
# 不输出日志
docker container run --name=report_server --network qq_robot --ip 172.20.0.9 -v $(pwd)/server_log:/usr/src/app/log -d -p 44551:44551 -it qq_server:0.0.2
