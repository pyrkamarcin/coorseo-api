#!/usr/bin/env bash

docker-compose exec application python3.8 migration.py db upgrade
