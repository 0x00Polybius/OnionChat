#!/bin/bash

# Onion Chat by Gegenwind
#   ____                               _           _ 
#  / ___| ___  __ _  ___ _ ____      _(_)_ __   __| |
# | |  _ / _ \/ _` |/ _ \ '_ \ \ /\ / / | '_ \ / _` |
# | |_| |  __/ (_| |  __/ | | \ V  V /| | | | | (_| |
#  \____|\___|\__, |\___|_| |_|\_/\_/ |_|_| |_|\__,_|
#             |___/                                  
#
# Installs all necessary packages

sudo apt-get update
sudo apt-get upgrade
sudo apt-get -y install tor python python2.7 python-pygame idle-python2.7
python OnionChat.pyw
