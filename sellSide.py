from pyparsing import tokenMap
from web3 import Web3
import config
import time
import requests
import time
import database
import universalFunctions

# Chain initialization
web3 = Web3(Web3.WebsocketProvider(config.infura_url))
contract = web3.eth.contract(address=config.pancakeSwap_factory, abi=config.pancakeSwap_factory_abi)
contract2 = web3.eth.contract(address=config.pancakeSwap_router, abi=config.pancakeSwap_router_abi)

def sellToken(tokenAddress, sellPercent, estimatedBNBValue):
    # Checksum token address
    tokenAddress = web3.toChecksumAddress(tokenAddress)
    # Generate token contract
    tokenContract = web3.eth.contract(tokenAddress, abi=config.tokenAbi)
    # Determine how much to sell (85%)
    tokenValue = tokenContract.functions.balanceOf(config.walletAddress).call()
    tokenValue = int(tokenValue * sellPercent)
    # Generate sell order
    pancakeswap2_txn = contract2.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
        tokenValue, 
        0, 
        [tokenAddress, config.addresses['WBNB']], 
        config.walletAddress, 
        (int(time.time()) + 900)
        ).buildTransaction(
            {
            'from': config.walletAddress,
            'gasPrice': Web3.toWei('5', 'gwei'),
            'nonce': web3.eth.get_transaction_count(config.walletAddress),
            }
        )
    # Sign sell order
    signedTxn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=config.privateKey)
    # Execute transaction
    txHash = Web3.toJSON(web3.eth.send_raw_transaction(signedTxn.rawTransaction))
    tokenMetadata = universalFunctions.getTokenData(tokenAddress)

    if sellPercent == 100:
        database.delete('Portfolio', 'tokenAddress', tokenAddress)
    else:
        database.updatePortfolio('transactionHash', txHash, 'tokenAddress', tokenAddress)
        database.updatePortfolio('buyPrice', tokenMetadata[2], 'tokenAddress', tokenAddress)
        database.updatePortfolio('estimatedSellPrice', "null", 'tokenAddress', tokenAddress)
        database.updatePortfolio('date', universalFunctions.getEpochTime(), 'tokenAddress', tokenAddress)
        database.updatePortfolio('transactions', int(database.read('Portfolio', 'tokenAddress', tokenAddress)[7]) + 1, 'tokenAddress', tokenAddress)

    # Append transaction to database
    database.appendTransaction(txHash, "S", tokenAddress, tokenMetadata[0], tokenMetadata[2], "{} {} / {} BNB".format(tokenValue, tokenMetadata[1], estimatedBNBValue), universalFunctions.getEpochTime())
    # Return transaction hash
    return txHash

def approve(tokenAddress):
    # Checksum token address
    tokenAddress = web3.toChecksumAddress(tokenAddress)
    # Generate token contract
    tokenContract = web3.eth.contract(address=tokenAddress, abi=config.tokenAbi)
    # Get contract allowance for token
    contractAllowance = tokenContract.functions.allowance(config.walletAddress, config.pancakeSwap_router).call()
    
    # Check if token is already allowed spender
    if contractAllowance < 0:
        # Generate allawance contract
        spender = config.pancakeSwap_router
        max_amount = web3.toWei(2**64-1,'ether')
        nonce = web3.eth.getTransactionCount(config.walletAddress)

        tx = tokenContract.functions.approve(spender, max_amount).buildTransaction({
            'from': config.walletAddress, 
            'gas': 6000000,
            'gasPrice': Web3.toWei('5', 'gwei'),
            'nonce': nonce
        })
        # Sign allawanace contract
        signed_tx = web3.eth.account.signTransaction(tx, config.privateKey)
        # Execute transaction and return hash
        txHash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tokenMetadata = universalFunctions.getTokenData(tokenAddress)
        # Append transaction to database
        database.appendTransaction(txHash, "A", tokenAddress, tokenMetadata[0], "null", "null", time.time.ctime)
        return web3.toHex(txHash)
    else:
        return None

def monitor(walletAddress):
    # For token in address
    tokens = requests.get('https://api.bscscan.com/api?module=account&action=tokentx&address={}&page=1&offset=10000&startblock=0&endblock=999999999&sort=asc&apikey=YourApiKeyToken'.format(walletAddress)).json()['result']
    tokenList = []
    # If token not recorded, record
    for token in tokens:
        if [web3.toChecksumAddress(token['contractAddress']), token['tokenDecimal']] not in tokenList:
            tokenList.append([web3.toChecksumAddress(token['contractAddress']), token['tokenDecimal']])
            
    multiplier = {
        '18': .000000000000000001,
        '9': .000000001,
        '8': .00000001,
        '6': .000001,
        '2': .01,
        '1': .1,
        '0': 1
    }

    portfolioTokenList = [] 
    for token in database.readAll('Portfolio'):
        portfolioTokenList.append(token[2])

    # For token in held tokens
    for tokenData in tokenList:
        # Checksum address
        tokenAddress = web3.toChecksumAddress(tokenData[0])
        # print(tokenAddress, portfolioTokenList[0])
        if tokenAddress in portfolioTokenList and tokenAddress not in ["0x0019450b0fb021ad2e9f7928101b171272cd537c"]:
            # Generate token contract
            tokenContract = web3.eth.contract(address=tokenAddress, abi=config.tokenAbi)
            # Get token balance
            tokenBalance = tokenContract.functions.balanceOf(config.walletAddress).call()
            if tokenBalance > 0:   
                tokenMetaData = universalFunctions.getTokenData(tokenAddress)
                # Calculate token bnb value
                bnbPrice = requests.get('https://qpkjpvpeqx.us-east-1.awsapprunner.com/api/v1/contract-events/token-metadata/{}'.format('0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')).json()['payload']['tokenMetadata']['bnbPrice']
                metaDataPayload = requests.get('https://qpkjpvpeqx.us-east-1.awsapprunner.com/api/v1/contract-events/token-metadata/{}'.format(tokenAddress)).json()
                tokenPrice = metaDataPayload['payload']['tokenMetadata']['tokenPrice']
                bnbValue = ((tokenBalance * multiplier[tokenData[1]]) * tokenPrice) / bnbPrice
                # If bnb value greater than criteria, sell 85%
                tokenPurchaseData = database.read('Portfolio', 'tokenAddress', tokenAddress)

                if int(tokenPurchaseData[7]) == 1:
                    bnbCriteria = .135

                if int(tokenPurchaseData[7]) == 2:
                    bnbCriteria = .1

                if int(tokenPurchaseData[7]) >= 3:
                    bnbCriteria = .05

                print('tokenName: {}\ntokenAddress: {}\ntokenBalance: {}\ntokenPrice: {}\nbnbValue:{}\nbnbCriteria: {}\n'.format(tokenMetaData[0], tokenAddress, tokenBalance * multiplier[tokenData[1]], tokenPrice, bnbValue, bnbCriteria))

                if bnbValue >= bnbCriteria:
                    try:
                        approve(tokenAddress)
                        print('approved...')
                    except:
                        pass
                    time.sleep(7)
                    sellToken(tokenAddress, .85, bnbValue / .85)
                    print('sold...')
                else:
                    buyEpochTime = int(tokenPurchaseData[6])
                    if buyEpochTime <= universalFunctions.getEpochTime() - 259200:
                        sellToken(tokenAddress, 1, bnbValue)

while True:
    try:
        print('--- Looping ---')
        monitor(config.walletAddress)
        time.sleep(7)
    except:
        pass
