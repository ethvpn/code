import logging

from listener import ContractListener
from ethjsonrpc import EthJsonRpc


logger = logging.getLogger(__name__)

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

client = EthJsonRpc('127.0.0.1', 8545)
anInstance = EntityUpdater(client)
anInstance.update_all()
