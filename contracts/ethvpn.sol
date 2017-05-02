pragma solidity ^0.4.10;
contract EthVPN{	
	address public owner;
	bool public locked; // in case the contract is locked
	uint public fees; // per-mille
	uint totalFees;
	mapping (address=>uint) balances;

	modifier onlyAddress (address _addr) {
        if (msg.sender != _addr)
            throw;
        _;
    }

	struct VPNInfo{
		string IPAddr; 	// give IP in plaintext initially
		uint bandwidth;		
		string country;	// the more detailed, the better
		address owner; 
		uint maxUsers; 	// the maximum number of parallel users
		uint currUsers; // the number of current users
		bool accepting; // if this still accepts new users
		uint fare;		// fare per hour, in wei		
	}

	struct VPNContract{
		uint VPNIndex;
		uint initialFare;
		uint starting;
		uint allottedTime;
		uint deposit;
		address user;
		bool terminated;
		string loginInfo;	
	}

	event NewRentRequest(uint VPNIndex, uint rentReq);
	event AcceptedRentRequest(uint rentReq, string loginInfo);
	event CanceledRentRequest(uint VPNIndex, uint rentReq);
	event TopupRentContract(uint rentReq);
	event CloseRentContract(uint rentReq);
	event TerminateRentContract(uint rentReq);
	event EnableLock();
	event DisableLock();
	event NewVPNListed(uint VPNIndex, address owner);

	VPNInfo[] public VPNs;
	VPNContract[] public contracts;


	function EthVPN(uint _fees){
		owner = msg.sender;
		locked = false;
		fees = _fees;
		totalFees = 0;
	}

	// ==== FUNCTIONs FOR A VPN =====
	function registerVPN(	string _IPAddr,
							uint _bandwidth,
							string _country, 
							uint _maxUsers, 
							bool _accepting,
							uint _fare) returns (bool success, uint VPNIndex){
		VPNs.push(VPNInfo({	IPAddr: _IPAddr,
							bandwidth: _bandwidth,
							country: _country,
							owner: msg.sender,
							maxUsers: _maxUsers,
							currUsers: 0,
							accepting: _accepting,
							fare: _fare}));
		NewVPNListed(VPNs.length-1, msg.sender);
		return (true, VPNs.length-1);
	}

	// adjust fare for VPNs[index], only applicable to new users
	function adjustFare(uint index, uint newFare) returns (bool){
		if (VPNs[index].owner != msg.sender)
			throw;
		VPNs[index].fare = newFare;
		return true;
	}

	// stop accepting rent requests
	function stopAccepting(uint i) returns (bool){
		if (VPNs[i].owner != msg.sender)
		    return false;
		VPNs[i].accepting = false;
		return true;
	}
	
	// start accepting rent requests
	function startAccepting(uint i) returns (bool){
		if (VPNs[i].owner != msg.sender)
		    return false;
		VPNs[i].accepting = true;
		return true;
	}


	// ========= FUNCTIONs for VPN USERs =============
	function requestToRentVPN(uint index) returns (bool success, uint reqIndex){
		if (index >= VPNs.length)
			throw;
		if (msg.value < VPNs[index].fare)
			throw;
		if (VPNs[index].currUsers == VPNs[index].maxUsers)
			throw;
		uint _allottedTime = msg.value/VPNs[index].fare;

		contracts.push(VPNContract(	{VPNIndex: index,
		                            initialFare: VPNs[index].fare,
									user: msg.sender,
									deposit: msg.value,
									terminated: false,
									starting: 0,
									allottedTime: _allottedTime,
									loginInfo: ''}));

		NewRentRequest(index, contracts.length-1);
		return (true, contracts.length-1);
	}

	// cancel some request to get money back
	function cancelRentRequest(uint reqIndex) returns (bool){
		if (reqIndex >= contracts.length)
			throw;
		if (contracts[reqIndex].user != msg.sender)
			throw;			
		if (contracts[reqIndex].starting != 0)
			throw;
		//check if the request has been terminated previously
		if (contracts[reqIndex].terminated)
			throw;
		contracts[reqIndex].terminated = true;
		// do not need to check the send
		// its the sender's responsibility to receive the refund
		msg.sender.send(contracts[reqIndex].deposit);
		CanceledRentRequest(contracts[reqIndex].VPNIndex, reqIndex);
		return true;
	}

	// top up some contract
	function topupRentContract(uint reqIndex) returns (bool){
		if (reqIndex >= contracts.length)
			throw;		
		if (contracts[reqIndex].terminated)
			throw;
		uint VPNIndex = contracts[reqIndex].VPNIndex;
		//do not allow top up VPN which has adjusted fare
		if (contracts[reqIndex].initialFare != VPNs[VPNIndex].fare)
			throw;

		contracts[reqIndex].deposit += msg.value;
		contracts[reqIndex].allottedTime += contracts[reqIndex].deposit/VPNs[VPNIndex].fare;
		TopupRentContract(reqIndex);
		return true;
	}

	// close the contract, and get the refund
	function closeRentContract(uint reqIndex) returns (bool){
		if (reqIndex >= contracts.length)
			throw;
		if (contracts[reqIndex].terminated)
			throw;
		if (contracts[reqIndex].user != msg.sender)
			throw;
		// if the request has not been approved, just refund
		if (contracts[reqIndex].starting == 0)
			return this.cancelRentRequest(reqIndex);

		uint usageTime = now - contracts[reqIndex].starting;
		uint VPNIndex = contracts[reqIndex].VPNIndex;
		uint refund = 0;
		uint totalCost = contracts[reqIndex].deposit;
		// check if there is any refund
		if (usageTime < contracts[reqIndex].allottedTime){
			totalCost = contracts[reqIndex].initialFare*((usageTime - contracts[reqIndex].allottedTime)/3600 + 1);			
			refund = contracts[reqIndex].deposit - totalCost;
		}
		balances[VPNs[VPNIndex].owner] += (totalCost*(1000-fees))/1000;
		totalFees += totalCost - (totalCost*(1000-fees))/1000;
		contracts[reqIndex].terminated = true;
		VPNs[VPNIndex].currUsers -= 1;
		if (refund > 0)
			msg.sender.send(refund);
		CloseRentContract(reqIndex);
		return true;
	}

	//========= Contract functions for VPN owner =====
	// cancel some request to get money back
	function acceptRentRequest(uint reqIndex, string _loginInfo) returns (bool){
		if (reqIndex >= contracts.length)
			throw;
		if (contracts[reqIndex].starting != 0)
			throw;
		//check if the request has been terminated previously
		if (contracts[reqIndex].terminated)
			throw;
		uint VPNIndex = contracts[reqIndex].VPNIndex;
		if (VPNs[VPNIndex].owner != msg.sender)
			throw;
		
		contracts[reqIndex].starting = now;
		contracts[reqIndex].loginInfo = _loginInfo;
		VPNs[VPNIndex].currUsers += 1;
		AcceptedRentRequest(reqIndex, _loginInfo);
		return true;
	}

	// after the allottedTime, owner can terminate the contract and get the fare
	function terminateRentContract(uint reqIndex) returns (bool){
		if (reqIndex >= contracts.length)
			throw;
		if (contracts[reqIndex].terminated)
			throw;		
		// if the request has not been approved, throw;
		if (contracts[reqIndex].starting == 0)
			throw;
		if (contracts[reqIndex].user != msg.sender)
			throw;
		uint usageTime = now - contracts[reqIndex].starting;
		uint VPNIndex = contracts[reqIndex].VPNIndex;
		// owner can only terminate after the alloted time
		if (! (usageTime > contracts[reqIndex].allottedTime &&
				msg.sender == VPNs[VPNIndex].owner))
			throw;
		// credit balance to the owner
		uint totalCost = contracts[reqIndex].deposit;
		balances[VPNs[VPNIndex].owner] += (totalCost*(1000-fees))/1000;
		totalFees += totalCost - (totalCost*(1000-fees))/1000;
		contracts[reqIndex].terminated = true;
		VPNs[VPNIndex].currUsers -= 1;
		TerminateRentContract(reqIndex);
		return true;
	}

	// other public function
	function getBalance() constant returns (uint){
		return balances[msg.sender];
	}

	function ownerWithdraw() returns (bool){
		if (balances[msg.sender] > 0){
			uint amount = balances[msg.sender];
			balances[msg.sender] = 0;
			msg.sender.send(amount);			
		}
		return true;
	}

	

	function getVPNInfo(uint VPNIndex) public constant returns (	string IPAddr,
														uint bandwidth,		
														string country,
														address owner,
														uint maxUsers,
														uint currUsers,
														bool accepting,
														uint fare){
		if (VPNIndex >= VPNs.length)
			throw;
		VPNInfo vpn = VPNs[VPNIndex];
		return (vpn.IPAddr, 
				vpn.bandwidth,
				vpn.country,
				vpn.owner,
				vpn.maxUsers,
				vpn.currUsers,
				vpn.accepting,
				vpn.fare);
	}

	function getNumberOfVPN() public constant returns (uint){
		return VPNs.length;
	}

	function getNumberOfReq() public constant returns (uint){
		return contracts.length;
	}

	//========= PLATFORM functions ==========
	function adjustFees(uint _newfees) onlyAddress(owner) returns (bool){
		fees = _newfees;
		return true;
	}
	
	function disableLock() onlyAddress(owner) returns (bool){
		locked = false;
		return true;
	}
	
	function enableLock() onlyAddress(owner) returns (bool){
		locked = true;
		return true;
	}
	
	function changeOwner(address newOwner) onlyAddress(owner) returns (bool){
	    owner = newOwner;
	    return true;
	}

	function collectFees(address toAddr) onlyAddress(owner) returns (bool){
		owner.send(totalFees);
		return true;
	}

	function(){ 
		throw; // don't expect anything here
	}
}