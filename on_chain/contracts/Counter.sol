// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract Counter is Ownable {
    uint256 private _count;

    event Incremented(uint256 newCount);    constructor() Ownable(msg.sender) {
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
