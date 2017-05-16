import logging
import string
import json
from web3 import Web3, KeepAliveRPCProvider, IPCProvider
import random
import sys
from web3.utils.compat import (
    Timeout,
)
unlockpassword = "smartpool"

def rands(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def genNewAccount():
    username = rands(6)
    password = rands(8)
    loginInfo = username + " " + password
    return loginInfo

class EntityUpdater:

    def __init__(self, web3):
        self.web3 = web3
        self.web3.eth.defaultAccount = self.web3.eth.coinbase
        ethvpnAddress = "0x369b2e33549445db7e676504efd3ba7aee5896ba"
        json_data=open("ethvpn.json").read()
        contractABI = json.loads(json_data)
        self.ethvpn = web3.eth.contract(abi=contractABI, address=ethvpnAddress)

        self.events = {
            "NewVPNListed": "NewVPNListed(uint256,address)",
            "NewRentRequest": "event NewRentRequest(uint256,address,uint256);",
            "TopupRentContract": "TopupRentContract(uint256)",
            "CloseRentContract": "CloseRentContract(uint256)",
            "TerminateRentContract": "TerminateRentContract(uint256)",
            "AcceptedRentRequest": "AcceptedRentRequest(uint256,string)"
        }        



if __name__ == '__main__':
    # web3 = EthJsonRpc('127.0.0.1', 8545)
    web3 = Web3(KeepAliveRPCProvider(host='localhost', port='8545'))    
    anInstance = EntityUpdater(web3)    
    web3.eth.defaultAccount = web3.eth.coinbase
    ethvpnAddress = "0x369b2e33549445db7e676504efd3ba7aee5896ba"
    json_data=open("ethvpn.json").read()
    contractABI = json.loads(json_data)
    ethvpn = web3.eth.contract(abi=contractABI, address=ethvpnAddress)

    while True:
        input_line = raw_input("command: ")        
        if input_line == "exit" or input_line == "quit":
            break
        else:
            args = input_line.split()
            # print args
            # list all vpns available
            if args[0] == "list-vpns":
                print "Listing all VPNS\n"
                no_vpns = ethvpn.call().getNumberOfVPN()
                print "The number of VPNs: %d\n" %no_vpns
                for index in range(no_vpns):                    
                    print "VPN %s info:"%index + str(ethvpn.call().getVPNInfo(index))

            # register a VPN
            elif args[0] == "register":
                print "Register a new VPN"
                if len(args) != 7:
                    print "Invalid. Expecting 6 arguments: IP, bandwidth, region, maxuser, accepting, fare per hour \n"
                else:
                    print "Registering a VPN at IP: %s, bandwidth %s Mbps, region %s, maxuser %s, accepting: %s, fare %s per hour \n"\
                %(args[1], args[2], args[3], args[4], args[5], args[6])
                web3.personal.unlockAccount(web3.eth.coinbase, unlockpassword)
                txAddr = ethvpn.transact({'from': web3.eth.coinbase, 'gas': 2000000}).registerVPN(str(args[1]),\
                    int(args[2]), str(args[3]), int(args[4]), bool(int(args[5])), int(args[6]))
                print "Done, TX's ID: %s\n" %txAddr

            # view all requests
            elif args[0] == "list-reqs":
                print "List all requests"
                if len(args) == 2:
                    print "List all requests to VPNs %s\n" %(args[1])
                else:
                    print "Invalid. Expecting a VPN index\n"
                no_reqs = ethvpn.call().getNumberOfReq()
                print "Total requests: %d\n" %no_reqs
                for index in range(no_reqs):
                    print "VPN %s info:"%index + str(ethvpn.call().getVPNInfo(index))


            #send rent request
            elif args[0] == "send-req":
                if len(args) != 3:
                    print "Invalid! Expect 2 arguments: VPNIndex and amount\n"
                    continue
                print "Sending request to rent VPN %s with %s ETH\n" %(args[1], args[2])
                web3.personal.unlockAccount(web3.eth.accounts[1], unlockpassword)
                txAddr = ethvpn.transact({'from': web3.eth.coinbase, 'value': web3.toWei(int(args[2]), "ether"), 'gas': 1000000}).requestToRentVPN(int(args[1]))
                print "Done, TX's ID: %s\n" %txAddr

            #view status of rent request
            elif args[0] == "view-req":
                if len(args) != 2:
                    print "Invalid! Expect 1 arguments: VPNIndex."
                    continue
                print "Viewing status of rent request no: %s\n" %(args[1])

            # accept a rent request
            elif args[0] == "acc-req":
                if len(args) != 3:
                    print "Invalid! Expect 2 arguments: reqIndex and loginInfo.\n"
                    continue
                print "Accepting rent request no: %s with loginInfo %s\n" %(args[1], args[2])
                
                web3.personal.unlockAccount(web3.eth.coinbase, unlockpassword)
                txAddr = ethvpn.transact({'from': web3.eth.coinbase, 'gas': 1000000}).acceptRentRequest(int(args[1]), args[2])
                print "Done, TX's ID: %s\n" %txAddr

            #terminate a contract
            elif args[0] == "terminate":
                if len(args) != 2:
                    print "Invalid! Expect 1 arguments: VPNIndex."
                    continue
                print "Terminating contract no: %s\n" %(args[1])
            else:
                print "Invalid command!\n"