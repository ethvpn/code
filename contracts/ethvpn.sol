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

    event NewVPNListed(uint VPNIndex, address indexed owner);
	event NewRentRequest(uint VPNIndex, address indexed owner, uint rentReq);
	event AcceptedRentRequest(uint rentReq, address indexed owner, string loginInfo, address indexed user);
	event CanceledRentRequest(uint VPNIndex, address indexed owner, uint rentReq);
	event TopupRentContract(uint rentReq, address indexed owner, address indexed user);
	event CloseRentContract(uint rentReq, address indexed owner, address indexed user);
	event TerminateRentContract(uint rentReq, address indexed owner, address indexed user);
	event EnabledLock();
	event DisabledLock();
	event OwnerWithdraw(address owner, uint amount);

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
							uint _fare) public returns (bool success, uint VPNIndex){
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
	function adjustFare(uint index, uint newFare) public returns (bool){
		if (VPNs[index].owner != msg.sender)
			throw;
		VPNs[index].fare = newFare;
		return true;
	}

	// stop accepting rent requests
	function stopAccepting(uint i) public returns (bool){
		if (VPNs[i].owner != msg.sender)
		    return false;
		VPNs[i].accepting = false;
		return true;
	}
	
	// start accepting rent requests
	function startAccepting(uint i) public returns (bool){
		if (VPNs[i].owner != msg.sender)
		    return false;
		VPNs[i].accepting = true;
		return true;
	}


	// ========= FUNCTIONs for VPN USERs =============
	function requestToRentVPN(uint index) payable public returns (bool success, uint reqIndex){
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

		NewRentRequest(index, VPNs[index].owner, contracts.length-1);
		return (true, contracts.length-1);
	}

	// cancel some request to get money back
	function cancelRentRequest(uint reqIndex) public returns (bool){
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
		uint VPNIndex = contracts[reqIndex].VPNIndex;
		CanceledRentRequest(contracts[reqIndex].VPNIndex, VPNs[VPNIndex].owner, reqIndex);
		return true;
	}

	// top up some contract
	function topupRentContract(uint reqIndex) payable public returns (bool){
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
		TopupRentContract(reqIndex, VPNs[VPNIndex].owner, msg.sender);
		return true;
	}

	// close the contract, and get the refund
	function closeRentContract(uint reqIndex) public returns (bool){
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
		CloseRentContract(reqIndex, VPNs[VPNIndex].owner, msg.sender);
		return true;
	}

	//========= Contract functions for VPN owner =====
	// cancel some request to get money back
	function acceptRentRequest(uint reqIndex, string _loginInfo) public returns (bool){
		if (reqIndex >= contracts.length)
			throw;
		// terminate if the request has been accepted
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
		AcceptedRentRequest(reqIndex, VPNs[VPNIndex].owner, _loginInfo,  contracts[reqIndex].user);
		return true;
	}

	// after the allottedTime, owner can terminate the contract and get the fare
	function terminateRentContract(uint reqIndex) public returns (bool){
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
		TerminateRentContract(reqIndex, VPNs[VPNIndex].owner, msg.sender);
		return true;
	}

	// other public function
	function getBalance() public constant returns (uint){
		return balances[msg.sender];
	}

	function ownerWithdraw() public returns (bool){
		if (balances[msg.sender] > 0){
			uint amount = balances[msg.sender];
			balances[msg.sender] = 0;	
			msg.sender.send(amount);
			OwnerWithdraw(msg.sender, amount);
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

	function getReqInfo(uint reqIndex) public constant returns (uint VPNIndex,
														uint amount,																
														address user,
														bool approved,
														string loginInfo,
														bool terminated){
		if (reqIndex >= contracts.length)
			throw;
		// uint VPNIndex = contracts[reqIndex].VPNIndex;
		// Con vpn = VPNs[VPNIndex];
		return (contracts[reqIndex].VPNIndex, 
				contracts[reqIndex].deposit,
				contracts[reqIndex].user,
				contracts[reqIndex].starting != 0,
				contracts[reqIndex].loginInfo,
				contracts[reqIndex].terminated);
	}

	//========= PLATFORM functions ==========
	function adjustFees(uint _newfees) onlyAddress(owner) public returns (bool){
		fees = _newfees;
		return true;
	}
	
	function disableLock() onlyAddress(owner) public returns (bool){
		locked = false;
		DisabledLock();
		return true;
	}
	
	function enableLock() onlyAddress(owner) public returns (bool){
		locked = true;
		EnabledLock();
		return true;
	}

	function getLock() public constant returns (bool){
		return locked;
	}
	
	function changeOwner(address newOwner) onlyAddress(owner) public returns (bool){
	    owner = newOwner;
	    return true;
	}

	function collectFees(address toAddr) onlyAddress(owner) public returns (bool){
		owner.send(totalFees);
		return true;
	}

	function(){ 
		throw; // don't expect anything here
	}
}