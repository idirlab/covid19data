#!/bin/bash
# V1
# March 28, 2020
# written by Josue Caraballo (josue.caraballo@mavs.uta.edu)
# This script should be run as sudo on idir-server8.
# It:
#  1) Reads a config file to identify a private key to send to git for authentication
#  2) Pushes updates to git
# Runs every day at 2AM
# Assumes master branch is set
cd /home/zhengyuan/Projects/covid19data
source gittoken.env
BRANCH=master
git add .
git commit -m "Syncing Project to Git on branch: $BRANCH"
git push deployment-origin $BRANCH
