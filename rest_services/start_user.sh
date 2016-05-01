#!/bin/bash
./wait-for-it.sh postgres:5432
python user_service.py