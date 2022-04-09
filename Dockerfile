FROM debian:latest

ENV DEBIAN_FRONTEND=noninteractive
LABEL maintainer="tait@bytetools.ca"
RUN apt update
RUN apt install -y nginx
RUN apt install -y python3
RUN apt install -y git
RUN apt install -y python3-pip
RUN apt install -y python3-venv
RUN apt install -y mariadb-client
RUN apt install -y mariadb-server
RUN apt install -y mariadb-backup
RUN apt install -y libmariadb-dev
WORKDIR "/root"
# how do I change this to git on deployment?
ADD . /root/schedule
WORKDIR "/root/schedule"
RUN rm -rf env
RUN python3 -m venv env
RUN . env/bin/activate
RUN pip3 install -r requirements.txt
