import logging

from userclient import ContractListener
from ethjsonrpc import EthJsonRpc


logger = logging.getLogger(__name__)

class EntityUpdater:

    def __init__(self, client):
        self.client = client
        self.events = {
            "NewVPNListed": "NewVPNListed(uint256,address)",            
            "NewRentRequest": "NewRentRequest(uint256,uint 256)",
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

        if event == self.events["VerifyTokenSet"]:
            txid = api_data["transactionHash"]
            print "new tx created txid: %s\n" %txid
        elif event == self.events["NewVPNListed"]:
            print api_data
            # index = api_data["topics"][1]
            # owner = api_data["topics"][2]
            # txid = api_data["transactionHash"]
            # print "new VPN listed in txid: %s\n" % txid
            # print "VPN number %s listed by" %(index, owner)
        else:
            raise RuntimeError("Unknown event: {}".format(event))

    def update_all(self):
        """Poll geth and get updates for the contracts in our database."""
        updates = 0


        # Get list of all known contracts in the database
        contracts = ["0x12b8e248e6e831d649108c4d231757dc6da3d64a"]

        # Each callback will run in its own db transaction context
        for c in contracts:
            updates += self.contract_listener.monitor_contract(c)

        updates += self.contract_listener.poll()

        return updates

client = EthJsonRpc('127.0.0.1', 8545)
anInstance = EntityUpdater(client)
anInstance.update_all()
