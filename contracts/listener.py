"""Poll Ethereum blockchain, install log hooks to call contracts.

Using geth JSON RPC API: https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newfilter

Copyright 2016 Mikko Ohtamaa - Licensed under MIT license.
"""


import logging
# from typing import Callable, Iterable, List, Optional
import datetime


from ethjsonrpc import EthJsonRpc
#require pysha3
from sha3 import keccak_256

#: Default logger
logging.basicConfig()
_logger = logging.getLogger(__name__)


#: Called when we spot a fired event. Callback is (contract_address, event_signature, api_data)
# callback_type = Callable[[str, str, dict], None]


class ContractStatus:
    """Hold information about the processing status of a single contract."""

    def __init__(self, filter_id, last_updated_at):
        self.filter_id = filter_id
        self.last_updated_at = last_updated_at


def now():
    """Get the current time as timezone-aware UTC timestamp."""
    return datetime.datetime.now()


def calculate_event_signature(decl):
    """Calculate bytecode signature of an event Solidy declaration.

    Example:

    .. code-block:

        assert calculate_event_signature("VerifyTokenSet(address,uint256)") == "3D2E225F28C7AAA8014B84B0DD267E297CB25A0B24CB02AB9C9FCF76F660F05F"

    To verify signature from the contract push opcodes:

    .. code-block:: console

        solc contract.sol --asm

    To debug transactions on Morden testnet

    * https://morden.ether.camp/transaction/9685191fece0dd0ef5a02210a305738be3fceb4089003924bc53de0cce0c0103

    http://solidity.readthedocs.io/en/latest/contracts.html#events

    https://github.com/ethereum/wiki/wiki/Solidity-Features#events
    """
    # print "0x" + keccak_256(decl.encode("utf-8")).hexdigest()
    return "0x" + keccak_256(decl.encode("utf-8")).hexdigest()


class ContractListener:
    """Fetch updates on events Solidy contract posts to Ethereum blockchain.

    """

    def __init__(self, client, events, callback, logger=_logger):
        """Create a contract listener.

        Callbacks look like:

        .. code-block:: python

            def cb(address, event, api_data)
                pass

        :param client: EthJsonRpc instance we use to connect to geth node
        :param events: List of Solidy event signatures we want to listne like like ``["Transfer(address,address,uint256)]``
        :param callback: Callable that's going to get called for every new event detected.
        :param logger: Optional
        """
        self.logger = _logger
        self.client = client
        self.events = events
        self.callback = callback
        self.event_signatures = {calculate_event_signature(e): e for e in events}

        #: Mapping contract address -> ContractStatus
        self.currently_monitored_contracts = {}

    def install_filter(self, contract_address):
        """Set up event filtering for a single contract using eth_newFilter.

        :param contract_address: hex string
        """

        installed_filter_id = self.client.eth_newFilter(from_block=0, address=contract_address)
        status = ContractStatus(filter_id=installed_filter_id, last_updated_at=None)
        self.currently_monitored_contracts[contract_address] = status

    def process_events(self, status, changes):

        updates = 0

        # Nothing changed
        if changes is None:
            self.logger.info("Nothing here")
            return 0

        for change in changes:
            contract_address = change["address"]

            if contract_address not in self.currently_monitored_contracts:
                self.logger.warn("Received a change for non-monitored contract %s", contract_address)
                continue

            topics = change["topics"]
            if not topics:
                self.logger.warn("Did not get topics with change data %s", change)
                continue

            event_type = topics[0]
            # self.logger.warn("event signature: %s", event_type)
            if event_type not in self.event_signatures:
                self.logger.warn("Unknown event signature %s", change)
                continue

            try:
                self.callback(contract_address, self.event_signatures[event_type], change)
                updates += 1
            except Exception as e:
                # IF we have bad code for processing one contract, don't stop at that but keep pushing for others
                self.logger.error("Failed to update contract %s", contract_address)
                self.logger.exception(e)

        status.last_updated_at = now()

        return updates

    def fetch_all(self, contract):
        status = self.currently_monitored_contracts[contract]
        filter_id = status.filter_id

        # Signature different as for newFilter :(
        changes = self.client.eth_getLogs(dict(fromBlock=0, address=contract))
        return self.process_events(status, changes)

    def fetch_changes(self, contract):
        """Fetch latest events from geth.

        .. note ::

                The some transction might be posted twice due to ramp up and poll calls running differently.
                Always make sure callbacks handle this.

        :param contracts: List of contract addresses as hex string we are interested in

        :return: Number of callbacks made
        """
        status = self.currently_monitored_contracts[contract]
        filter_id = status.filter_id
        changes = self.client.eth_getFilterChanges(filter_id=filter_id)
        return self.process_events(status, changes)

    def monitor_contract(self, contract_address):
        """Start monitoring a contract and run callback for its all past events.

        If contract is already added do nothing.

        :param contract_address:
        :return: Number of triggered callbacks
        """
        assert type(contract_address) == str
        assert contract_address.startswith("0x")
        contract_address = contract_address.lower()

        if contract_address in self.currently_monitored_contracts:
            return 0

        self.install_filter(contract_address)

        return self.fetch_all(contract_address)

    def remove_contract(self, contract_address):
        del self.currently_monitored_contracts[contract_address]

    def poll(self):
        """Fetch changes to all monitored contracts.

        Note that some events might be posted twice due to time elapse between ``monitor_contract`` and ``poll``.

        :return: Number of triggered callbacks
        """
        updates = 0
        for c in self.currently_monitored_contracts.keys():
            updates += self.fetch_changes(c)
        return updates