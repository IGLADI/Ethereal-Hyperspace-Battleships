#!/bin/sh

if ! which mariadb > /dev/null 2>&1
then
    printf '%s\n' 'mariadb not found.'
    exit 1
fi

if  [ "$(id -u)" -ne 0 ]
then
    printf '%s\n' 'not running as root.'
    exit 1
fi

printf '%s\n' 'Setting up ethb'
mariadb < setup_ethb.sql 
printf '%s\n' 'Setting up database'
mariadb < setup_database.sql
