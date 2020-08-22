#!/usr/bin/env bash

imageversion='0.0.1'
imagename="mail_report_system"
image="$imagename:$imageversion"
containername="mail_report_system_server"
ip="172.19.0.155"
exportport=49991
dockernetwork="base-mysql-database-network"

docker container stop "$containername"
docker container rm "$containername"
docker image rm "$image"
docker image build -t "$image" .
# 输出日志
docker container run --name "$containername" --network "$dockernetwork" --ip "$ip" -v $(pwd)/server_log:/usr/src/app/log -p "$exportport:$exportport" "$image"
# 不输出日志
#docker container run --name "$containername" --network "$dockernetwork" --ip "$ip" -v $(pwd)/server_log:/usr/src/app/log -d -p "$exportport:$exportport" -it "$image"
