#!/bin/sh

# only needed for the print statement
REMOTE='localhost'
USER='ethb'
DATABASE='ethbdb'
PASSWORD='space123'
PORT='3306'

die () { >&2 printf '%s\n' "$@"; exit 1; }


mariadb_command="mariadb --host='$REMOTE' --user='$USER' --password='$PASSWORD' --port='$PORT' '$DATABASE'"
if ! which mariadb > /dev/null
then
    printf 'No mariadb client installed.\n Continue? [Enter]'
    read -r continue
fi

[ "$continue" ] && exit 1

if [ "$1" = "docker" ]
then
    [ "$(id -u)" -ne 0 ] && die 'Run as root.'
    docker ps > /dev/null 2>&1 || die 'Docker not running?'
    docker build -t mariadb .
    docker compose up -d
elif [ "$1" = "local" ]
then
    [ "$(id -u)" -ne 0 ] && die 'Run as root.'
    mariadb < sql/ethb.sql
    eval "$mariadb_command" < sql/tables.sql
elif [ "$1" = "tables" ]
then
    eval "$mariadb_command" < sql/tables.sql
else
    die 'usage: ./install.sh <docker|remote|table>'
fi
printf 'Succeeded.\n'

printf "To access the database run:\n%s\n^\n" "$mariadb_command"
