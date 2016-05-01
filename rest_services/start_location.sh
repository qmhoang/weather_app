#!/bin/bash
./wait-for-it.sh postgres:5432
./wait-for-it.sh user_service:5000
python location_service.py