// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Sustainable Food Supply Chain
 * @dev Manages the entire food supply chain including users, products, operations, quality control, sustainability metrics, and CO2 tokens.
 * @notice This contract is intended for demonstration purposes and not for production use.
 */
contract SustainableFoodSupplyChain {
    // ==================== STRUCTS ====================

    // User Registry Structs
    struct User {
        string name;
        string email;
        string role; // "PRODUCER", "DISTRIBUTOR", "RETAILER", "CONSUMER"
        bool isActive;
        uint256 registrationDate;
    }

    // Product Registry Structs
    struct Product {
        uint256 productId;
        string name;
        string description;
        string category;
        string unit;
        address producer;
        uint256 createdAt;
        bool isActive;
        string metadata; // Certificazioni, standard di qualità, etc.
    }

    // Product Request Structs
    struct Request {
        uint256 requestId;
        address requester;
        string productName;
        uint256 quantity;
        string unit;
        uint256 deadline;
        string status; // "PENDING", "ACCEPTED", "REJECTED", "COMPLETED"
        uint256 createdAt;
        uint256 updatedAt;
    }

    // Operation Registry Structs
    struct Operation {
        uint256 operationId;
        address operator;
        string operationType; // "PRODUCTION", "PROCESSING", "TRANSPORT", "STORAGE", "DISTRIBUTION"
        string description;
        string location;
        uint256 timestamp;
        string status; // "IN_PROGRESS", "COMPLETED", "CANCELLED"
        string metadata; // JSON string with additional data
    }

    // Quality Control Structs
    struct QualityCheck {
        uint256 checkId;
        uint256 productId;
        address inspector;
        string checkType; // "CERTIFICATION", "INSPECTION", "TEST"
        string result; // "PASS", "FAIL", "PENDING"
        string details;
        uint256 timestamp;
        string metadata; // Risultati dettagliati, certificazioni, etc.
    }

    // Sustainability Metrics Structs
    struct Metric {
        uint256 metricId;
        uint256 productId;
        address reporter;
        string metricType; // "CARBON_FOOTPRINT", "WATER_USAGE", "ENERGY_CONSUMPTION", "WASTE_REDUCTION"
        uint256 value;
        string unit;
        string methodology;
        uint256 timestamp;
        string metadata; // Dettagli aggiuntivi sulla metodologia, certificazioni, etc.
    }

    // Action Log Struct
    struct ActionLog {
        uint256 actionId;
        string actionType;
        address initiatedBy;
        uint256 timestamp;
        string details;
    }

    // ==================== STATE VARIABLES ====================
    
    // General variables
    address public owner;
    mapping(address => bool) public authorizedOperators;
    uint256 private actionCounter = 0;
    mapping(uint256 => ActionLog) public actionLogs;

    // User Registry variables
    mapping(address => User) private users;
    mapping(address => bool) private isRegistered;

    // Product Registry variables
    uint256 private productCounter;
    mapping(uint256 => Product) private products;
    mapping(address => uint256[]) private producerProducts;
    mapping(string => uint256[]) private categoryProducts;

    // Product Request variables
    uint256 private requestCounter;
    mapping(uint256 => Request) private requests;
    mapping(address => uint256[]) private userRequests;

    // Operation Registry variables
    uint256 private operationCounter;
    mapping(uint256 => Operation) private operations;
    mapping(address => uint256[]) private userOperations;

    // Quality Control variables
    uint256 private checkCounter;
    mapping(uint256 => QualityCheck) private qualityChecks;
    mapping(uint256 => uint256[]) private productChecks;
    mapping(address => uint256[]) private inspectorChecks;

    // Sustainability Metrics variables
    uint256 private metricCounter;
    mapping(uint256 => Metric) private metrics;
    mapping(uint256 => uint256[]) private productMetrics;
    mapping(address => uint256[]) private reporterMetrics;
    mapping(string => uint256[]) private typeMetrics;

    // CO2 Token variables
    string public tokenName = "CO2 Token";
    string public tokenSymbol = "CO2";
    uint8 public tokenDecimals = 18;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    // ==================== EVENTS ====================

    // General events
    event OperatorAuthorized(address indexed operator);
    event OperatorRevoked(address indexed operator);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    // User Registry events
    event UserRegistered(address indexed userAddress, string name, string role);
    event UserUpdated(address indexed userAddress, string name, string role);
    event UserDeactivated(address indexed userAddress);

    // Product Registry events
    event ProductCreated(uint256 indexed productId, address indexed producer, string name);
    event ProductUpdated(uint256 indexed productId, string name);
    event ProductDeactivated(uint256 indexed productId);

    // Product Request events
    event RequestCreated(uint256 indexed requestId, address indexed requester, string productName);
    event RequestStatusUpdated(uint256 indexed requestId, string newStatus);
    event RequestCompleted(uint256 indexed requestId);

    // Operation Registry events
    event OperationCreated(uint256 indexed operationId, address indexed operator, string operationType);
    event OperationStatusUpdated(uint256 indexed operationId, string newStatus);
    event OperationMetadataUpdated(uint256 indexed operationId, string metadata);

    // Quality Control events
    event QualityCheckCreated(uint256 indexed checkId, uint256 indexed productId, address indexed inspector);
    event QualityCheckUpdated(uint256 indexed checkId, string result);
    event QualityCheckCompleted(uint256 indexed checkId);

    // Sustainability Metrics events
    event MetricRecorded(uint256 indexed metricId, uint256 indexed productId, string metricType);
    event MetricUpdated(uint256 indexed metricId, uint256 newValue);
    event MetricVerified(uint256 indexed metricId, address verifier);

    // CO2 Token events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);

    // ==================== CONSTRUCTOR ====================

    constructor() {
        owner = msg.sender;
        authorizedOperators[owner] = true;
    }

    // ==================== MODIFIERS ====================

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedOperators[msg.sender] || msg.sender == owner, "Not authorized");
        _;
    }

    modifier onlyRegistered() {
        require(isRegistered[msg.sender], "User not registered");
        _;
    }

    modifier validProduct(uint256 _productId) {
        require(products[_productId].productId != 0, "Product does not exist");
        _;
    }

    modifier validRequest(uint256 _requestId) {
        require(requests[_requestId].requestId != 0, "Request does not exist");
        _;
    }

    modifier validOperation(uint256 _operationId) {
        require(operations[_operationId].operationId != 0, "Operation does not exist");
        _;
    }

    modifier validCheck(uint256 _checkId) {
        require(qualityChecks[_checkId].checkId != 0, "Quality check does not exist");
        _;
    }

    modifier validMetric(uint256 _metricId) {
        require(metrics[_metricId].metricId != 0, "Metric does not exist");
        _;
    }

    // ==================== GENERAL FUNCTIONS ====================

    function authorizeOperator(address _operator) external onlyOwner {
        require(_operator != address(0), "Invalid operator address");
        require(!authorizedOperators[_operator], "Operator already authorized");
        
        authorizedOperators[_operator] = true;
        emit OperatorAuthorized(_operator);
    }

    function revokeOperator(address _operator) external onlyOwner {
        require(authorizedOperators[_operator], "Operator not authorized");
        
        authorizedOperators[_operator] = false;
        emit OperatorRevoked(_operator);
    }

    function logAction(string memory _actionType, address _initiator, string memory _details) internal {
        actionCounter++;
        actionLogs[actionCounter] = ActionLog(actionCounter, _actionType, _initiator, block.timestamp, _details);
        emit ActionLogged(actionCounter, _actionType, _initiator, block.timestamp, _details);
    }

    // ==================== USER REGISTRY FUNCTIONS ====================

    function registerUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external {
        require(!isRegistered[msg.sender], "User already registered");
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_email).length > 0, "Email cannot be empty");
        require(bytes(_role).length > 0, "Role cannot be empty");

        users[msg.sender] = User({
            name: _name,
            email: _email,
            role: _role,
            isActive: true,
            registrationDate: block.timestamp
        });

        isRegistered[msg.sender] = true;
        logAction("Create", msg.sender, "User registered");
        emit UserRegistered(msg.sender, _name, _role);
    }

    function updateUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external onlyRegistered {
        require(users[msg.sender].isActive, "User is not active");
        
        users[msg.sender].name = _name;
        users[msg.sender].email = _email;
        users[msg.sender].role = _role;

        logAction("Update", msg.sender, "User updated");
        emit UserUpdated(msg.sender, _name, _role);
    }

    function deactivateUser() external onlyRegistered {
        require(users[msg.sender].isActive, "User already deactivated");
        users[msg.sender].isActive = false;
        logAction("Update", msg.sender, "User deactivated");
        emit UserDeactivated(msg.sender);
    }

    function getUser(address _userAddress) external view returns (
        string memory name,
        string memory email,
        string memory role,
        bool isActive,
        uint256 registrationDate
    ) {
        require(isRegistered[_userAddress], "User not registered");
        User memory user = users[_userAddress];
        return (user.name, user.email, user.role, user.isActive, user.registrationDate);
    }

    function isUserRegistered(address _userAddress) external view returns (bool) {
        return isRegistered[_userAddress];
    }

    // ==================== PRODUCT REGISTRY FUNCTIONS ====================

    function createProduct(
        string memory _name,
        string memory _description,
        string memory _category,
        string memory _unit,
        string memory _metadata
    ) external onlyRegistered returns (uint256) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_category).length > 0, "Category cannot be empty");
        require(bytes(_unit).length > 0, "Unit cannot be empty");

        productCounter++;
        uint256 productId = productCounter;

        products[productId] = Product({
            productId: productId,
            name: _name,
            description: _description,
            category: _category,
            unit: _unit,
            producer: msg.sender,
            createdAt: block.timestamp,
            isActive: true,
            metadata: _metadata
        });

        producerProducts[msg.sender].push(productId);
        categoryProducts[_category].push(productId);

        logAction("Create", msg.sender, "Product created");
        emit ProductCreated(productId, msg.sender, _name);
        return productId;
    }

    function updateProduct(
        uint256 _productId,
        string memory _name,
        string memory _description,
        string memory _category,
        string memory _unit,
        string memory _metadata
    ) external validProduct(_productId) {
        Product storage product = products[_productId];
        require(product.producer == msg.sender, "Only producer can update product");
        require(product.isActive, "Product is not active");

        product.name = _name;
        product.description = _description;
        product.category = _category;
        product.unit = _unit;
        product.metadata = _metadata;

        logAction("Update", msg.sender, "Product updated");
        emit ProductUpdated(_productId, _name);
    }

    function deactivateProduct(uint256 _productId) external validProduct(_productId) {
        Product storage product = products[_productId];
        require(product.producer == msg.sender, "Only producer can deactivate product");
        require(product.isActive, "Product already deactivated");

        product.isActive = false;
        logAction("Update", msg.sender, "Product deactivated");
        emit ProductDeactivated(_productId);
    }

    function getProduct(uint256 _productId) external view validProduct(_productId) returns (
        uint256 productId,
        string memory name,
        string memory description,
        string memory category,
        string memory unit,
        address producer,
        uint256 createdAt,
        bool isActive,
        string memory metadata
    ) {
        Product memory product = products[_productId];
        return (
            product.productId,
            product.name,
            product.description,
            product.category,
            product.unit,
            product.producer,
            product.createdAt,
            product.isActive,
            product.metadata
        );
    }

    function getProducerProducts(address _producer) external view returns (uint256[] memory) {
        return producerProducts[_producer];
    }

    function getCategoryProducts(string memory _category) external view returns (uint256[] memory) {
        return categoryProducts[_category];
    }

    // ==================== PRODUCT REQUEST FUNCTIONS ====================

    function createRequest(
        string memory _productName,
        uint256 _quantity,
        string memory _unit,
        uint256 _deadline
    ) external onlyRegistered returns (uint256) {
        require(bytes(_productName).length > 0, "Product name cannot be empty");
        require(_quantity > 0, "Quantity must be greater than 0");
        require(bytes(_unit).length > 0, "Unit cannot be empty");
        require(_deadline > block.timestamp, "Deadline must be in the future");

        requestCounter++;
        uint256 requestId = requestCounter;

        requests[requestId] = Request({
            requestId: requestId,
            requester: msg.sender,
            productName: _productName,
            quantity: _quantity,
            unit: _unit,
            deadline: _deadline,
            status: "PENDING",
            createdAt: block.timestamp,
            updatedAt: block.timestamp
        });

        userRequests[msg.sender].push(requestId);
        logAction("Create", msg.sender, "Request created");
        emit RequestCreated(requestId, msg.sender, _productName);
        return requestId;
    }

    function updateRequestStatus(uint256 _requestId, string memory _newStatus) 
        external 
        validRequest(_requestId) 
        onlyAuthorized 
    {
        Request storage request = requests[_requestId];
        require(
            keccak256(bytes(_newStatus)) == keccak256(bytes("ACCEPTED")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("REJECTED")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("COMPLETED")),
            "Invalid status"
        );

        request.status = _newStatus;
        request.updatedAt = block.timestamp;

        logAction("Update", msg.sender, "Request status updated");
        emit RequestStatusUpdated(_requestId, _newStatus);
        
        if (keccak256(bytes(_newStatus)) == keccak256(bytes("COMPLETED"))) {
            emit RequestCompleted(_requestId);
        }
    }

    function getRequest(uint256 _requestId) 
        external 
        view 
        validRequest(_requestId) 
        returns (
            uint256 requestId,
            address requester,
            string memory productName,
            uint256 quantity,
            string memory unit,
            uint256 deadline,
            string memory status,
            uint256 createdAt,
            uint256 updatedAt
        ) 
    {
        Request memory request = requests[_requestId];
        return (
            request.requestId,
            request.requester,
            request.productName,
            request.quantity,
            request.unit,
            request.deadline,
            request.status,
            request.createdAt,
            request.updatedAt
        );
    }

    function getUserRequests(address _user) external view returns (uint256[] memory) {
        return userRequests[_user];
    }

    // ==================== OPERATION REGISTRY FUNCTIONS ====================

    function createOperation(
        string memory _operationType,
        string memory _description,
        string memory _location,
        string memory _metadata
    ) external onlyRegistered returns (uint256) {
        require(bytes(_operationType).length > 0, "Operation type cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(bytes(_location).length > 0, "Location cannot be empty");

        operationCounter++;
        uint256 operationId = operationCounter;

        operations[operationId] = Operation({
            operationId: operationId,
            operator: msg.sender,
            operationType: _operationType,
            description: _description,
            location: _location,
            timestamp: block.timestamp,
            status: "IN_PROGRESS",
            metadata: _metadata
        });

        userOperations[msg.sender].push(operationId);
        logAction("Create", msg.sender, "Operation created");
        emit OperationCreated(operationId, msg.sender, _operationType);
        return operationId;
    }

    function updateOperationStatus(uint256 _operationId, string memory _newStatus)
        external
        validOperation(_operationId)
    {
        Operation storage operation = operations[_operationId];
        require(operation.operator == msg.sender || authorizedOperators[msg.sender], "Not authorized");
        require(
            keccak256(bytes(_newStatus)) == keccak256(bytes("IN_PROGRESS")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("COMPLETED")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("CANCELLED")),
            "Invalid status"
        );

        operation.status = _newStatus;
        logAction("Update", msg.sender, "Operation status updated");
        emit OperationStatusUpdated(_operationId, _newStatus);
    }

    function updateOperationMetadata(uint256 _operationId, string memory _metadata)
        external
        validOperation(_operationId)
    {
        Operation storage operation = operations[_operationId];
        require(operation.operator == msg.sender || authorizedOperators[msg.sender], "Not authorized");
        operation.metadata = _metadata;
        logAction("Update", msg.sender, "Operation metadata updated");
        emit OperationMetadataUpdated(_operationId, _metadata);
    }

    function getOperation(uint256 _operationId)
        external
        view
        validOperation(_operationId)
        returns (
            uint256 operationId,
            address operator,
            string memory operationType,
            string memory description,
            string memory location,
            uint256 timestamp,
            string memory status,
            string memory metadata
        )
    {
        Operation memory operation = operations[_operationId];
        return (
            operation.operationId,
            operation.operator,
            operation.operationType,
            operation.description,
            operation.location,
            operation.timestamp,
            operation.status,
            operation.metadata
        );
    }

    function getUserOperations(address _user) external view returns (uint256[] memory) {
        return userOperations[_user];
    }

    // ==================== QUALITY CONTROL FUNCTIONS ====================

    function createQualityCheck(
        uint256 _productId,
        string memory _checkType,
        string memory _details,
        string memory _metadata
    ) external onlyRegistered returns (uint256) {
        require(bytes(_checkType).length > 0, "Check type cannot be empty");
        require(bytes(_details).length > 0, "Details cannot be empty");

        checkCounter++;
        uint256 checkId = checkCounter;

        qualityChecks[checkId] = QualityCheck({
            checkId: checkId,
            productId: _productId,
            inspector: msg.sender,
            checkType: _checkType,
            result: "PENDING",
            details: _details,
            timestamp: block.timestamp,
            metadata: _metadata
        });

        productChecks[_productId].push(checkId);
        inspectorChecks[msg.sender].push(checkId);

        logAction("Create", msg.sender, "Quality check created");
        emit QualityCheckCreated(checkId, _productId, msg.sender);
        return checkId;
    }

    function updateQualityCheck(
        uint256 _checkId,
        string memory _result,
        string memory _details,
        string memory _metadata
    ) external validCheck(_checkId) {
        QualityCheck storage check = qualityChecks[_checkId];
        require(check.inspector == msg.sender || authorizedOperators[msg.sender], "Not authorized");
        require(
            keccak256(bytes(_result)) == keccak256(bytes("PASS")) ||
            keccak256(bytes(_result)) == keccak256(bytes("FAIL")) ||
            keccak256(bytes(_result)) == keccak256(bytes("PENDING")),
            "Invalid result"
        );

        check.result = _result;
        check.details = _details;
        check.metadata = _metadata;

        logAction("Update", msg.sender, "Quality check updated");
        emit QualityCheckUpdated(_checkId, _result);

        if (
            keccak256(bytes(_result)) == keccak256(bytes("PASS")) ||
            keccak256(bytes(_result)) == keccak256(bytes("FAIL"))
        ) {
            emit QualityCheckCompleted(_checkId);
        }
    }

    function getQualityCheck(uint256 _checkId) external view validCheck(_checkId) returns (
        uint256 checkId,
        uint256 productId,
        address inspector,
        string memory checkType,
        string memory result,
        string memory details,
        uint256 timestamp,
        string memory metadata
    ) {
        QualityCheck memory check = qualityChecks[_checkId];
        return (
            check.checkId,
            check.productId,
            check.inspector,
            check.checkType,
            check.result,
            check.details,
            check.timestamp,
            check.metadata
        );
    }

    function getProductQualityChecks(uint256 _productId) external view returns (uint256[] memory) {
        return productChecks[_productId];
    }

    function getInspectorQualityChecks(address _inspector) external view returns (uint256[] memory) {
        return inspectorChecks[_inspector];
    }

    // ==================== SUSTAINABILITY METRICS FUNCTIONS ====================

    function recordMetric(
        uint256 _productId,
        string memory _metricType,
        uint256 _value,
        string memory _unit,
        string memory _methodology,
        string memory _metadata
    ) external onlyRegistered returns (uint256) {
        require(bytes(_metricType).length > 0, "Metric type cannot be empty");
        require(bytes(_unit).length > 0, "Unit cannot be empty");
        require(bytes(_methodology).length > 0, "Methodology cannot be empty");

        metricCounter++;
        uint256 metricId = metricCounter;

        metrics[metricId] = Metric({
            metricId: metricId,
            productId: _productId,
            reporter: msg.sender,
            metricType: _metricType,
            value: _value,
            unit: _unit,
            methodology: _methodology,
            timestamp: block.timestamp,
            metadata: _metadata
        });

        productMetrics[_productId].push(metricId);
        reporterMetrics[msg.sender].push(metricId);
        typeMetrics[_metricType].push(metricId);

        logAction("Create", msg.sender, "Sustainability metric recorded");
        emit MetricRecorded(metricId, _productId, _metricType);
        return metricId;
    }

    function updateMetric(
        uint256 _metricId,
        uint256 _value,
        string memory _methodology,
        string memory _metadata
    ) external validMetric(_metricId) {
        Metric storage metric = metrics[_metricId];
        require(metric.reporter == msg.sender || authorizedOperators[msg.sender], "Not authorized");

        metric.value = _value;
        metric.methodology = _methodology;
        metric.metadata = _metadata;

        logAction("Update", msg.sender, "Sustainability metric updated");
        emit MetricUpdated(_metricId, _value);
    }

    function verifyMetric(uint256 _metricId) external validMetric(_metricId) onlyAuthorized {
        logAction("Verify", msg.sender, "Sustainability metric verified");
        emit MetricVerified(_metricId, msg.sender);
    }

    function getMetric(uint256 _metricId) external view validMetric(_metricId) returns (
        uint256 metricId,
        uint256 productId,
        address reporter,
        string memory metricType,
        uint256 value,
        string memory unit,
        string memory methodology,
        uint256 timestamp,
        string memory metadata
    ) {
        Metric memory metric = metrics[_metricId];
        return (
            metric.metricId,
            metric.productId,
            metric.reporter,
            metric.metricType,
            metric.value,
            metric.unit,
            metric.methodology,
            metric.timestamp,
            metric.metadata
        );
    }

    function getProductMetrics(uint256 _productId) external view returns (uint256[] memory) {
        return productMetrics[_productId];
    }

    function getReporterMetrics(address _reporter) external view returns (uint256[] memory) {
        return reporterMetrics[_reporter];
    }

    function getTypeMetrics(string memory _metricType) external view returns (uint256[] memory) {
        return typeMetrics[_metricType];
    }

    // ==================== CO2 TOKEN FUNCTIONS ====================
    
    function totalSupply() public view returns (uint256) {
        return 1000000 * 10**uint256(tokenDecimals); // Initial supply of 1M tokens
    }
    
    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }
    
    function transfer(address recipient, uint256 amount) public returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }
    
    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }
    
    function approve(address spender, uint256 amount) public returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address sender, address recipient, uint256 amount) public returns (bool) {
        _transfer(sender, recipient, amount);
        _approve(sender, msg.sender, _allowances[sender][msg.sender] - amount);
        return true;
    }
    
    function rewardCompensatoryAction(uint256 amount) public onlyAuthorized {
        _mint(msg.sender, amount);
        logAction("Reward", msg.sender, "CO2 compensatory action rewarded");
    }
    
    function processOperationCO2(uint256 consumedCO2, uint256 thresholdCO2) public returns (bool) {
        if (consumedCO2 < thresholdCO2) {
            uint256 rewardAmount = thresholdCO2 - consumedCO2;
            _mint(msg.sender, rewardAmount);
            logAction("Reward", msg.sender, "CO2 efficiency rewarded");
            return true;
        } else if (consumedCO2 > thresholdCO2) {
            uint256 penaltyAmount = consumedCO2 - thresholdCO2;
            require(_balances[msg.sender] >= penaltyAmount, "Insufficient tokens for CO2 penalty");
            _burn(msg.sender, penaltyAmount);
            logAction("Penalty", msg.sender, "CO2 inefficiency penalized");
            return true;
        }
        return false;
    }
    
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "Transfer from zero address");
        require(recipient != address(0), "Transfer to zero address");
        require(_balances[sender] >= amount, "Insufficient balance");
        
        _balances[sender] -= amount;
        _balances[recipient] += amount;
        emit Transfer(sender, recipient, amount);
    }
    
    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "Approve from zero address");
        require(spender != address(0), "Approve to zero address");
        
        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }
    
    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "Mint to zero address");
        
        _balances[account] += amount;
        emit TokensMinted(account, amount);
        emit Transfer(address(0), account, amount);
    }
    
    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "Burn from zero address");
        require(_balances[account] >= amount, "Burn amount exceeds balance");
        
        _balances[account] -= amount;
        emit TokensBurned(account, amount);
        emit Transfer(account, address(0), amount);
    }
}
