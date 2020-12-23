FROM ubuntu:18.04

LABEL maintainer="someone@gmail.com"

ENV MYSQL_USER=mysql \
    MYSQL_VERSION=5.7 \
    MYSQL_DATA_DIR=/var/lib/mysql \
    MYSQL_RUN_DIR=/run/mysqld \
    MYSQL_LOG_DIR=/var/log/mysql \
    DB_REMOTE_ROOT_NAME=Jesualdo \
    DB_REMOTE_ROOT_PASS=Jesualdo2020 \
    DB_REMOTE_ROOT_HOST=127.0.0.1 \
    DB_NAME=coviddb \
    DB_USER=Jesualdo \
    DB_PASS=Jesualdo2020

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server=${MYSQL_VERSION}* \
 && rm -rf ${MYSQL_DATA_DIR} \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .

COPY entrypoint.sh /sbin/entrypoint.sh

RUN apt-get update && apt-get install -y python3-pip && apt-get install -y git && apt-get install -y nano && apt-get install -y libmysqlclient-dev

RUN pip3 install flask && pip3 install mysql && pip3 install pandas

RUN pip3 install mysql-connector
RUN pip3 install requests
RUN pip3 install gitpython
RUN pip3 install schedule
RUN pip3 install -U scikit-learn
RUN pip3 install numpy
RUN pip3 install joblib
RUN pip3 install Flask-Limiter
RUN pip3 install pyjwt
RUN pip3 install Werkzeug
RUN pip3 install Flask-Cors==1.10.3

RUN chmod 755 /sbin/entrypoint.sh

EXPOSE 3306/tcp

ENTRYPOINT ["/sbin/entrypoint.sh"]

CMD ["/usr/bin/mysqld_safe"]