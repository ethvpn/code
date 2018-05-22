_Warning: EthVPN is only in alpha stage.  Don't use it for anything important._

# ethvpn
The package for running a VPN connection with ShadowSocks via Ethereum.

# Usage
## Step 1. Connect to Rinkeby testnet
The `ethvpn` contract is currently deployed on Rinkeby testnet at this address `0x71f3abc045c3e73010ef46042553c66bb7f7a320`. Thus, you need to sync your node to Rinkeby testnet before using the client. Follow the instructions to sync with Rinkeby here https://www.rinkeby.io/

## Step 2. Start your node
You need to start your fullnode with `rpc` and the  "db,eth,net,web3,personal" rpc-apis enabled. Particularly, since currently only Geth supports Rinkeby, you need to run:

```
geth --rinkeby --datadir=.rinkeby --ethstats='ethvpn:Respect my authoritah!@stats.rinkeby.io' --bootnodes=enode://a24ac7c5484ef4ed0c5eb2d36620ba4e4aa13b8c84684e1b4aab0cebea2ae45cb4d375b77eab56516d34bfbd3c1a833fc51296ff084b770b94fb9028c4d25ccf@52.169.42.101:30303?discport=30304 --rpc --rpcapi "db,eth,net,web3,personal"
```

## Step 3. Change your pass-phrase to unlock your account
The client is using the first address, e.g. `eth.accounts[0]`, so you need to replace the `ethvpn` value in this line
```
unlockpassword = "ethvpn"
```
to your pass-phrase to unlock the first address.

## Step 4. Run the client.

Simply run
```
cd contracts
python client.py
```
It will ask you to key in the command and the corresponding parameters.
Currently we support the following commands (all indexes start from 0).

1. `list-vpns`, to list all available VPNs, expecting 0 argument.
Output: a list of `n` tuples, each represent the following info of a VPN:
```
string IPAddr, uint bandwidth, string country, address owner, uint maxUsers, uint currUsers, bool accepting, uint fare
```
2. `register`, to register a new vpn, expecting 6 arguments: IP, bandwidth, region, maxuser, accepting, fare per hour
e.g.
```
command: register 127.0.0.1 100 Singapore 10 1 100
```
3. `list-reqs`, to list all request to rent a VPN.
Return a list of `m` tuples, each represents the following info of a request:
```
uint VPNIndex, uint amount, address user, bool approved, string loginInfo, bool terminated (if approved)
```
4. `send-req`, to send a request to rent a VPN, expecting 2 arguments VPN index and the deposit amount (in ETH).
e.g.
```
command: send-req 0 0.1
```
5. `acc-req`, for the vpn's owner to accept a request, expect 2 arguments: request index and the login-info
e.g.
```
command: acc-req 0 username-password
```

6. `close-contract`, for a user to close a contract that was started by him/her (A request is approved will be called a contract.)
e.g.
```
command: close-contract 0
```

---

```
geth --networkid=4 --datadir=your-data-dir --syncmode=light --ethstats='ethvpn:Respect my authoritah!@stats.rinkeby.io' --bootnodes=enode://a24ac7c5484ef4ed0c5eb2d36620ba4e4aa13b8c84684e1b4aab0cebea2ae45cb4d375b77eab56516d34bfbd3c1a833fc51296ff084b770b94fb9028c4d25ccf@52.169.42.101:30303?discport=30304 --rpc --rpcapi "db,eth,net,web3,personal"
```




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
