// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleCounter {
    uint256 private _count;
    address private _owner;

    event Incremented(uint256 newCount);

    modifier onlyOwner() {
        require(msg.sender == _owner, "Not the owner");
        _;
    }

    constructor() {
        _owner = msg.sender;
        _count = 0;
    }

    function increment() public onlyOwner {
        _count += 1;
        emit Incremented(_count);
    }

    function getCount() public view returns (uint256) {
        return _count;
    }
}
