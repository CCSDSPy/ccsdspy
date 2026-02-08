#!bin/sh
pytest  -v --cov-report term --cov-report html:htmlcov --cov-report xml --cov-fail-under=95 --cov=ccsdspy
