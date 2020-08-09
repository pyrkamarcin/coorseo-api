#!/usr/bin/env bash

docker-compose exec backend python3.8 migration.py db upgrade
