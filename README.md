_Warning: EthVPN is only in alpha stage.  Don't use it for anything important._

# ethvpn
The package for running a VPN connection with ShadowSocks via Ethereum.




# Usage: server

There are many versions/forks of Shadowsocks.  For this project, specific ones are required.  You must get exactly these:

1. [shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev)
2. [shadowsocks-manager](https://github.com/shadowsocks/shadowsocks-manager)

Then one can run `run_ss-manager` which runs `ss-manager` which runs `ss-server`.  Then you use `edit_ss.py` to add/remove accounts from the ss-server.


# Usage: client

As far as we know clients can use any version of Shadowsocks, but the recommended one is [shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev).  Then from your server you'll need:

1. The server IP address
2. The server's encryption method
3. Your personal port and personal password


Then from the terminal (or using a GUI like [ShadowsocksX-NG](https://github.com/shadowsocks/ShadowsocksX-NG)), type:

`$ ss-local -s SERVER_IP -m SERVER_ENCRYPTION_METHOD -p YOUR_PORT -k YOUR_PASSWORD -l 1337`

The `-l 1337` can be any local port of your choice.  Then, while ss-local is running, you open your operating system's proxy setting and specify a SOCKS5 proxy on IP address `127.0.0.1` (localhost) using local port `1337`.  No username and password.

And Voila.  You're done.

----
# Related Work

Aka: possible front-ends.

* [uproxy](http://uproxy.org)
* [Streisand](https://github.com/jlund/streisand)
* [ShadowSocks](https://github.com/shadowsocks/shadowsocks-libev)
* [ShadowVPN](https://github.com/clowwindy/ShadowVPN)
* [Mysterium](http://mysterium.network)
* [Hola](https://hola.org)
