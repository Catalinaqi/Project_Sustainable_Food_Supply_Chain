const SimpleCounter = artifacts.require("SimpleCounter");

module.exports = async function (deployer) {
  try {
    await deployer.deploy(SimpleCounter);
    const instance = await SimpleCounter.deployed();
    console.log("Counter deployed to:", instance.address);
  } catch (error) {
    console.error("Error deploying Counter:", error);
    throw error;
  }
};
