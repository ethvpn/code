#!/bin/sh


ss_manager_address=/var/run/ss-manager.sock
ss_server_config=cfg/ss_server.json

my_ip_address=$(dig +short myip.opendns.com @resolver1.opendns.com.)

echo "- Start ss-server on public IP $my_ip_address"
echo "-- config file: $ss_server_config..."
echo "- Opening manager interface on $ss_manager_address"

ss-manager --manager-address $ss_manager_address --executable $(which ss-server) -c $ss_server_config
#ss-manager --manager-address $ss_manager_address --executable $(which ss-server)

echo "Done!"
