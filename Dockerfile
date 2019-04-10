FROM ubuntu:latest

ARG user=jenkins
ARG group=jenkins
ARG uid=1000
ARG gid=1000

ENV QA_HOME /opt/qa

RUN apt-get update && \
    apt-get install -y ant python3 python3-pip python3-dev libmysqlclient-dev && \
    pip3 install jira mysqlclient TestLink-API-Python-client && \
    groupadd -g ${gid} ${group} && \
    useradd -u ${uid-} -g ${group} -s /bin/bash ${user} && \
    mkdir -p $QA_HOME && \
    chown $user:$group $QA_HOME

WORKDIR /opt/qa

USER jenkins
