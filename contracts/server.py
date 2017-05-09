import logging
import string
from listener import ContractListener
from ethjsonrpc import EthJsonRpc
import random

logger = logging.getLogger(__name__)
# ethvpnAddress = "0x3f989ec10cec3fd4d6794ac5f7cb327c12e2161e"
# ethvpnContract = web3.eth.contract([{"constant":true,"inputs":[],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"VPNs","outputs":[{"name":"IPAddr","type":"string"},{"name":"bandwidth","type":"uint256"},{"name":"country","type":"string"},{"name":"owner","type":"address"},{"name":"maxUsers","type":"uint256"},{"name":"currUsers","type":"uint256"},{"name":"accepting","type":"bool"},{"name":"fare","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"index","type":"uint256"},{"name":"newFare","type":"uint256"}],"name":"adjustFare","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"enableLock","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"reqIndex","type":"uint256"}],"name":"terminateRentContract","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"ownerWithdraw","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"contracts","outputs":[{"name":"VPNIndex","type":"uint256"},{"name":"initialFare","type":"uint256"},{"name":"starting","type":"uint256"},{"name":"allottedTime","type":"uint256"},{"name":"deposit","type":"uint256"},{"name":"user","type":"address"},{"name":"terminated","type":"bool"},{"name":"loginInfo","type":"string"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"reqIndex","type":"uint256"}],"name":"closeRentContract","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"i","type":"uint256"}],"name":"startAccepting","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_IPAddr","type":"string"},{"name":"_bandwidth","type":"uint256"},{"name":"_country","type":"string"},{"name":"_maxUsers","type":"uint256"},{"name":"_accepting","type":"bool"},{"name":"_fare","type":"uint256"}],"name":"registerVPN","outputs":[{"name":"success","type":"bool"},{"name":"VPNIndex","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"VPNIndex","type":"uint256"}],"name":"getVPNInfo","outputs":[{"name":"IPAddr","type":"string"},{"name":"bandwidth","type":"uint256"},{"name":"country","type":"string"},{"name":"owner","type":"address"},{"name":"maxUsers","type":"uint256"},{"name":"currUsers","type":"uint256"},{"name":"accepting","type":"bool"},{"name":"fare","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"reqIndex","type":"uint256"}],"name":"topupRentContract","outputs":[{"name":"","type":"bool"}],"payable":true,"type":"function"},{"constant":false,"inputs":[{"name":"reqIndex","type":"uint256"},{"name":"_loginInfo","type":"string"}],"name":"acceptRentRequest","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"getNumberOfVPN","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"getNumberOfReq","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_newfees","type":"uint256"}],"name":"adjustFees","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"fees","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"toAddr","type":"address"}],"name":"collectFees","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"changeOwner","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"index","type":"uint256"}],"name":"requestToRentVPN","outputs":[{"name":"success","type":"bool"},{"name":"reqIndex","type":"uint256"}],"payable":true,"type":"function"},{"constant":false,"inputs":[{"name":"i","type":"uint256"}],"name":"stopAccepting","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"disableLock","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"locked","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"reqIndex","type":"uint256"}],"name":"cancelRentRequest","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"inputs":[{"name":"_fees","type":"uint256"}],"payable":false,"type":"constructor"},{"payable":false,"type":"fallback"},{"anonymous":false,"inputs":[{"indexed":false,"name":"VPNIndex","type":"uint256"},{"indexed":false,"name":"rentReq","type":"uint256"}],"name":"NewRentRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"rentReq","type":"uint256"},{"indexed":false,"name":"loginInfo","type":"string"}],"name":"AcceptedRentRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"VPNIndex","type":"uint256"},{"indexed":false,"name":"rentReq","type":"uint256"}],"name":"CanceledRentRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"rentReq","type":"uint256"}],"name":"TopupRentContract","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"rentReq","type":"uint256"}],"name":"CloseRentContract","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"rentReq","type":"uint256"}],"name":"TerminateRentContract","type":"event"},{"anonymous":false,"inputs":[],"name":"EnableLock","type":"event"},{"anonymous":false,"inputs":[],"name":"DisableLock","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"VPNIndex","type":"uint256"},{"indexed":false,"name":"owner","type":"address"}],"name":"NewVPNListed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"owner","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"OwnerWithdraw","type":"event"}])
# ethvpn = ethvpnContract(address=ethvpnAddress)

def rands(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def acceptRentRequest(client, reqId):
    username = rands(6)
    password = rands(8)
    loginInfo = username + " " + password



class EntityUpdater:

    def __init__(self, client):
        self.client = client
        self.events = {
            "NewVPNListed": "NewVPNListed(uint256,address)",
            "NewRentRequest": "NewRentRequest(uint256,uint256)",
            "TopupRentContract": "TopupRentContract(uint256)",
            "CloseRentContract": "CloseRentContract(uint256)",
            "TerminateRentContract": "TerminateRentContract(uint256)",
            "AcceptedRentRequest": "AcceptedRentRequest(uint256,string)"
        }

        self.contract_listener = ContractListener(self.client, self.events.values(), self.on_blockchain_event)

    def on_blockchain_event(self, address, event, api_data):
        """Called by ContractLister to tell us about the contract events.

        :param address: Contract address as a hex string
        :param event: One of event signatures
        :param api_data: eth_getFilterChanges() result https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterchanges
        :return:
        """
        logger.info("Received contract event %s for %s", event, address)

        if event == self.events["NewRentRequest"]:            
            data = api_data['data']
            vpn_id = int(data[:66], 0)
            req_id = int("0x"+data[66:], 0)
            print "New Rent Request to VPN with id: %d in request with ID: %d\n" %(vpn_id, req_id)


        elif event == self.events["NewVPNListed"]:
            data = api_data['data']
            vpn_id = int(data[:66], 0)
            owner_addr = "0x"+data[-40:]
            txid = api_data["transactionHash"]
            print "new VPN listed in txid: %s" % txid
            print "VPN number %d listed by %s\n" %(vpn_id, owner_addr)
        else:
            raise RuntimeError("Unknown event: {}".format(event))

    def update_all(self):
        """Poll geth and get updates for the contracts in our database."""
        updates = 0


        # Get list of all known contracts in the database
        contracts = ["0x3f989ec10cec3fd4d6794ac5f7cb327c12e2161e"]

        # Each callback will run in its own db transaction context
        for c in contracts:
            updates += self.contract_listener.monitor_contract(c)

        updates += self.contract_listener.poll()

        return updates

if __name__ == '__main__':
    client = EthJsonRpc('127.0.0.1', 8545)
    anInstance = EntityUpdater(client)
    anInstance.update_all()
