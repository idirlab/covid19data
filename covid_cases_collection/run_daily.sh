#!/bin/bash
# V1
# March 28, 2020
# written by Israa Jaradat (israa.jaradat@mavs.uta.edu)
# This is a script that runs thrice daily from crontab 
# It basically activates the virtual environment inside "covid19data/COVID_data_collection/ through sourcing covid19data/COVID_data_collection/covidvenv/bin/activate
# then runs python scripts to collect data 
cd /idir-covid19/covid19data/COVID_data_collection/
source covidvenv/bin/activate
cd /idir-covid19/covid19data/data_collection/src
sudo python collect_data.py -j -n -c > /idir-covid19/covid19data/data_collection/stdouterr.txt 2>&1
