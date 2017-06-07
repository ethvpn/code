#!/usr/bin/env python3

import string
import json
from web3 import Web3, KeepAliveRPCProvider, IPCProvider, HTTPProvider
import random, sys
import os.path

from web3.utils.compat import (
    Timeout,
)

from pprint import pprint
from binascii import hexlify

from ethereum import transactions
from ethereum.keys import decode_keystore_json
import rlp

###########################################################################
WALLET_FILENAME = '/Users/virgil/.rinkeby/keystore/UTC--2017-06-06T03-28-32.862694163Z--1fd8e0100a2e6e9514f7c65eb8d581f89a659795'
WALLET_PASSWORD = 'jvks9KXnztX'
WALLET_ADDRESS = '1fd8e0100a2e6e9514f7c65eb8d581f89a659795'
ETHVPN_CONTRACT_ADDRESS = '0x71f3abc045c3e73010ef46042553c66bb7f7a320'
INFURA_HOST = 'https://rinkeby.infura.io/NdB5PCo5IksWiI1KdMIw'
ETHVPN_ABI_FILENAME = 'ethvpn.json'

###########################################################################

def load_wallet( wallet_filename, password ):

    assert os.path.isfile( wallet_filename )

    with open( wallet_filename ) as f:
        wallet_json = json.load(f)

        address = wallet_json['address']
        priv_key = decode_keystore_json(wallet_json, password)

        return address, priv_key

def load_contractabi( abi_filename ):

    assert os.path.isfile( abi_filename )

    with open( abi_filename ) as f:
        z = json.load(f)

        return z



def genTransactionHex(target, wallet_privatekey, amount, nonce=0, gasprice=24000000000, startgas=21000):
    '''returns the hex representation of a transaction'''

    if type(target) is not bytes:
        target = bytes(target, 'utf-8')

    if type(nonce) is not int:
        nonce = int(nonce)

    if type(wallet_privatekey) is not bytes:
        target = bytes(target, 'utf-8')

    # if amount if a float digit, we presumably just meant it to be an integer
    if type(amount) is float and amount.isdigit():
        amount = int(amount)
    
    tx = transactions.Transaction(nonce, gasprice, startgas, target, amount, b'').sign(wallet_privatekey)

    z = hexlify( rlp.encode(tx) )

    return z






if __name__ == '__main__':
    # web3 = EthJsonRpc('127.0.0.1', 8545)

    #web3 = Web3( KeepAliveRPCProvider(host='localhost', port='8545') )
    infura = Web3( HTTPProvider(INFURA_HOST) )

    print("Connected to INFURA.")
    print("Latest Ethereum block:", infura.eth.blockNumber )


    wallet_address, wallet_privatekey = load_wallet( WALLET_FILENAME, WALLET_PASSWORD )
    contractABI = load_contractabi( ETHVPN_ABI_FILENAME )

    #target = '0x67e5d173BE803Ca97687498CD3F892BFaB54d12C'
    res = genTransactionHex( ETHVPN_CONTRACT_ADDRESS, wallet_privatekey, infura.toWei(0.1, 'ether') )

    print(res)

    #print('Wallet :: address:', WALLET_ADDRESS, '\t balance:', wallet_balance(WALLET_ADDRESS) )
    #print("accounts:", web3.eth.accounts )
    #print_local_wallets( web3.eth.accounts )

    sys.stdout.flush()
    
    infura.eth.defaultAccount = WALLET_ADDRESS
    
    ethvpn = infura.eth.contract(abi=contractABI, address=ETHVPN_CONTRACT_ADDRESS)

    while True:
        input_line = input("command: ")

        if not input_line:
            continue

        if input_line == "exit" or input_line == "quit":
            break

        args = input_line.split()

        # print args
        # list all vpns available
        if args[0] == "list-vpns":
            print( "Listing all VPNS\n" )
            no_vpns = ethvpn.call().getNumberOfVPN()
            print( "The number of VPNs: %d\n" % no_vpns )
            for index in range(no_vpns):                    
                print( "VPN", index, "info:", str(ethvpn.call().getVPNInfo(index)) )

        # register a VPN
        elif args[0] == "register":
            print( "Register a new VPN" )
            if len(args) != 7:
                print( "Invalid. Expecting 6 arguments: IP, bandwidth, region, maxuser, accepting, fare per hour \n" )
            else:
                print( "Registering a VPN at IP:", args[1], "bandwidth", args[1], "Mbps", args[2], "region", args[3], "maxuser", args[4], "accepting:", args[5], "fare", args[6], "per hour\n" )
            
            infura.personal.unlockAccount(web3.eth.defaultAccount, WALLET_PASSWORD)
            txAddr = ethvpn.transact({'from': web3.eth.defaultAccount, 'gas': 2000000}).registerVPN(str(args[1]),\
                int(args[2]), str(args[3]), int(args[4]), bool(int(args[5])), int(args[6]))
            print( "Done, TX's ID: %s\n" %txAddr )

        # view all requests
        elif args[0] == "list-reqs":
            if len(args) == 1:
                print( "List all requests" )
                no_reqs = ethvpn.call().getNumberOfReq()
                print( "Total requests: %d\n" %no_reqs )
                for index in range(no_reqs):
                    print( "VPN %s info:"%index + str(ethvpn.call().getReqInfo(index)) )
            else:
                print( "Invalid. Expecting a VPN index\n" )


        #send rent request
        elif args[0] == "send-req":
            if len(args) != 3:
                print( "Invalid! Expect 2 arguments: VPNIndex and amount\n" )
                continue

            print( "Sending request to rent VPN", args[1], "with", args[2], "ETH\n" )
            #txAddr = ethvpn.transact({'from': infura.eth.defaultAccount,
            # 'value': infura.toWei(), "ether"), 'gas': 1000000}).requestToRentVPN(int(args[1]))
            amount_wei = infura.toWei(float(args[2]), 'ether')

            raw_txn = genTransactionHex( ETHVPN_CONTRACT_ADDRESS, wallet_privatekey, amount_wei, startgas=1000000 )

            txAddr = infura.eth.sendRawTransaction( raw_txn )
            
            print( "Done, TX's ID:", txAddr , "\n" )

        #view status of rent request
        elif args[0] == "view-req":
            if len(args) != 2:
                print( "Invalid! Expect 1 arguments: reqIndex." )
                continue
            print( "Viewing status of rent request no:", args[1], "\n" )
            print( str(ethvpn.call().getReqInfo(int(args[1]))) )

        # accept a rent request
        elif args[0] == "acc-req":
            if len(args) != 3:
                print( "Invalid! Expect 2 arguments: reqIndex and loginInfo.\n" )
                continue
            print( "Accepting rent request no:", args[1], "with loginInfo", args[2], "\n" )
            
            infura.personal.unlockAccount(infura.eth.defaultAccount, WALLET_PASSWORD)
            txAddr = ethvpn.transact({'from': infura.eth.defaultAccount, 'gas': 1000000}).acceptRentRequest(int(args[1]), args[2])
            print( "Done, TX's ID: %s\n" % txAddr )

        #terminate a contract
        elif args[0] == "close-contract":
            if len(args) != 2:
                print( "Invalid! Expect 1 arguments: reqIndex." )
                continue
            print( "Closing contract no:", args[1], "\n" )
            infura.personal.unlockAccount(infura.eth.defaultAccount, WALLET_PASSWORD)
            txAddr = ethvpn.transact({'from': infura.eth.defaultAccount, 'gas': 1000000}).closeRentContract(int(args[1]))
            print( "Done, TX's ID: %s\n" %txAddr )
        else:
            print( "Invalid command!\n" )


