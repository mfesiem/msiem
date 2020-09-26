#!/bin/bash

python3 -m msiem -h > doc/README.txt
python3 -m msiem config -h > doc/CONFIG.txt
python3 -m msiem alarms -h > doc/ALARMS.txt
python3 -m msiem esm -h > doc/ESM.txt
python3 -m msiem ds -h > doc/DS.txt
python3 -m msiem events -h > doc/EVENTS.txt
python3 -m msiem api -h > doc/API.txt
python3 -m msiem wl -h > doc/WL.txt