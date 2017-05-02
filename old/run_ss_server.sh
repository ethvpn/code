#!/bin/sh

CFG_FILE="/root/cfg/ss_server.json"

# ssserver -c "$CFG_FILE"
ss-server -c "/root/cfg/ss_server.json" -v --manager-address /var/run/shadowsocks-manager.sock --fast-open

#       [--reuse-port]             Enable port reuse.
#       [--fast-open]              Enable TCP fast open.
