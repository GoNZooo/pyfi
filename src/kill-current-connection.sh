#!/bin/bash

# Don't need to kill dhcpcd because it can just run for the next connection 
sudo wpa_cli terminate
sudo killall dhcpcd
