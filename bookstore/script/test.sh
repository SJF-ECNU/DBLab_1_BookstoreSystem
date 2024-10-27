#!/bin/sh
export PYTHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data
coverage combine
coverage report --omit="be/app.py,fe/bench/run.py,fe/bench/session.py,fe/bench/workload.py"
coverage html
