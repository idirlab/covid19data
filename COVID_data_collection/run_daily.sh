#!/bin/bash
# V1
# March 28, 2020
# written by Israa Jaradat (israa.jaradat@mavs.uta.edu)
# This is a script that runs daily at 1 AM from crontab 
# It basically activates the virtual environment inside "covid19data/COVID_data_collection/ through sourcing covid19data/COVID_data_collection/covidvenv/bin/activate
# then runs python scripts to collect data 
cd /home/zhengyuan/Projects/covid19data/COVID_data_collection/
source covidvenv/bin/activate
cd src
sudo python collect_data.py
sudo python collect_global_data.py
sudo python add_to_time_series.py
