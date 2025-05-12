const CO2Token = artifacts.require("CO2Token");
const { expect } = require("chai");
const truffleAssert = require("truffle-assertions");

contract("CO2Token", function (accounts) {
  const owner = accounts[0];
  const user1 = accounts[1];
  const user2 = accounts[2];
  let tokenInstance;

  beforeEach(async function () {
    tokenInstance = await CO2Token.new({ from: owner });
  });

  describe("Funzionalità base del token", function () {
    it("dovrebbe avere nome, simbolo e decimali corretti", async function () {
      const name = await tokenInstance.name();
      const symbol = await tokenInstance.symbol();
      const decimals = await tokenInstance.decimals();
      
      expect(name).to.equal("CO2 Token");
      expect(symbol).to.equal("CO2");
      expect(decimals.toNumber()).to.equal(18);
    });

    it("dovrebbe permettere il trasferimento di token", async function () {
      // Prima creiamo dei token per l'utente
      await tokenInstance.rewardCompensatoryAction(1000, { from: user1 });
      const initialBalance = await tokenInstance.balanceOf(user1);
      
      // Trasferiamo i token ad un altro utente
      await tokenInstance.transfer(user2, 500, { from: user1 });
      
      // Verifichiamo i saldi
      const finalBalanceUser1 = await tokenInstance.balanceOf(user1);
      const finalBalanceUser2 = await tokenInstance.balanceOf(user2);
      
      expect(finalBalanceUser1.toNumber()).to.equal(initialBalance.toNumber() - 500);
      expect(finalBalanceUser2.toNumber()).to.equal(500);
    });
  });

  describe("Funzionalità CO2", function () {
    it("dovrebbe ricompensare con token per azioni compensative", async function () {
      const rewardAmount = 1000;
      await tokenInstance.rewardCompensatoryAction(rewardAmount, { from: user1 });
      
      const balance = await tokenInstance.balanceOf(user1);
      expect(balance.toNumber()).to.equal(rewardAmount);
    });

    it("dovrebbe gestire correttamente operazioni di CO2 sotto soglia", async function () {
      const consumedCO2 = 500;
      const thresholdCO2 = 1000;
      
      const result = await tokenInstance.processOperationCO2(consumedCO2, thresholdCO2, { from: user1 });
      truffleAssert.eventEmitted(result, 'TokensMinted');
      
      const balance = await tokenInstance.balanceOf(user1);
      expect(balance.toNumber()).to.equal(thresholdCO2 - consumedCO2);
    });

    it("dovrebbe gestire correttamente operazioni di CO2 sopra soglia", async function () {
      const initialAmount = 1000;
      await tokenInstance.rewardCompensatoryAction(initialAmount, { from: user1 });
      
      const consumedCO2 = 800;
      const thresholdCO2 = 500;
      
      const result = await tokenInstance.processOperationCO2(consumedCO2, thresholdCO2, { from: user1 });
      truffleAssert.eventEmitted(result, 'TokensBurned');
      
      const finalBalance = await tokenInstance.balanceOf(user1);
      expect(finalBalance.toNumber()).to.equal(initialAmount - (consumedCO2 - thresholdCO2));
    });
  });
}); 