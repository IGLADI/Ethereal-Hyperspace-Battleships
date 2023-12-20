FROM alpine:latest

# Dependencies
RUN apk update
RUN apk add mysql mysql-client

# Setup mariadb
RUN mysql_install_db --user=mysql --datadir=/var/lib/mariadb \
	&& mkdir -p /run/mysqld \
	&& chown -R mysql:mysql /run/mysqld \
	&& sed -i 's/^skip-networking/bind-address=0.0.0.0/' /etc/my.cnf.d/mariadb-server.cnf

COPY sql/ethb.sql sql/tables.sql /tmp/
COPY config/mariadb-server.sh /usr/local/bin/mariadb-server
COPY config/startup.sh /usr/local/bin/startup
RUN chmod +x /usr/local/bin/mariadb-server
RUN chmod +x /usr/local/bin/startup

# EXPOSE 3306

WORKDIR /etc/my.cnf.d/

CMD ["startup"]
