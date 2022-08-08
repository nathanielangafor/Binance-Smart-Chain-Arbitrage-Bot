if __name__ == '__main__':
    import requests
    import datetime
    from web3 import Web3
    import config
    import time
    import undetected_chromedriver.v2 as uc
    from selenium.webdriver.common.by import By
    import database
    import universalFunctions

    # Contract initialization
    web3 = Web3(Web3.WebsocketProvider(config.infura_url))
    contract = web3.eth.contract(address=config.pancakeSwap_factory, abi=config.pancakeSwap_factory_abi)
    contract2 = web3.eth.contract(address=config.pancakeSwap_router, abi=config.pancakeSwap_router_abi)

    def getEpochTime():
        t = time.time()
        return int(t)

    def buyToken(tokenAddress, amount):
        tx = contract2.functions.swapExactETHForTokens(
            0,
            [config.addresses['WBNB'], tokenAddress],
            config.addresses['recipient'],
            (int(time.time()) + 60)
        ).buildTransaction({
            'from': config.addresses['recipient'],
            'value': web3.toWei(float(amount), 'ether'),
            'gas': 3000000,
            'gasPrice': Web3.toWei('5', 'gwei'),
            'nonce': web3.eth.get_transaction_count(config.addresses['recipient']),
        })

        signed_tx = web3.eth.account.sign_transaction(tx, config.privateKey)
        txHash = Web3.toJSON(web3.eth.sendRawTransaction(signed_tx.rawTransaction))
        tokenMetadata = universalFunctions.getTokenData(tokenAddress)
        database.appendTransaction(str(txHash), "B", tokenAddress, tokenMetadata[0], 'null', "{} / {} BNB".format(tokenMetadata[1], amount), universalFunctions.getEpochTime())
        database.appendToPortfolio(txHash, tokenAddress, tokenMetadata[0], 'null', 'null', universalFunctions.getEpochTime())
        return txHash
        
    def initializeDriver():
        options = uc.ChromeOptions()
        options.add_argument('--user-data-dir=/Users/fnln/Desktop/moniMaker/Chrome Profile')
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        driver = uc.Chrome(options=options, version_main=101, enable_cdp_events=True)
        return driver

    def getTokenRating(tokenAddress):
        driver = initializeDriver()
        driver.get('https://tokensniffer.com/')

        retries = 0
        while 'Welcome!' not in driver.page_source():
            time.sleep(1)

            retries = retries + 1
            if retries >= 30:
                driver.quit()
                return '', ''

        driver.find_element(by=By.CLASS_NAME, value='Home_searchInput__1uxZk').send_keys(tokenAddress)
        
        while True:
            time.sleep(1)

            retries = retries + 1
            if retries >= 30:
                driver.quit()
                return '', ''
            try:
                driver.find_element(by=By.CLASS_NAME, value='Home_searchResult__3ZKTW').click()
                break
            except:
                    pass

        retries = 0
        while "captcha" not in driver.page_source():
            if "403 Forbidden" in driver.page_source():
                time.sleep(5)

            time.sleep(1)

            retries = retries + 1
            if retries >= 30:
                driver.quit()
                return '', ''

        driver.execute_script("""document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format('qwerqwerqwerqwer'))
        
        try:
            driver.execute_script(f"___grecaptcha_cfg.clients[0].L.L.callback('ƒ ()')")
        except:
            pass
        try:
            driver.execute_script(f"___grecaptcha_cfg.clients[0].S.S.callback('ƒ ()')")
        except:
            pass
        try:
            driver.execute_script(f"___grecaptcha_cfg.clients[0].X.X.callback('ƒ ()')")
        except:
            pass

        retries = 0
        while "Summary" not in driver.page_source():
            time.sleep(1)

            retries = retries + 1
            if retries >= 30:
                driver.quit()
                return '', ''
        
        source = driver.page_source()
        driver.quit()

        return str(source).split('Smell Test<!')[1].split('</span></h3><div class="')[0].split(';">')[1], str(source)


    def getTokenInfo(address):
        honeypotPayload = requests.get('https://qpkjpvpeqx.us-east-1.awsapprunner.com/api/v1/contract-events/token-honeypot-scan/{}'.format(address)).json()
        try:
            isHoneypot = honeypotPayload['payload']['data']['IsHoneypot']
        except:
            isHoneypot = True
            return [isHoneypot]
            
        MaxTxAmountBNB = honeypotPayload['payload']['data']['MaxTxAmountBNB']
        BuyTax = honeypotPayload['payload']['data']['BuyTax']
        SellTax = honeypotPayload['payload']['data']['SellTax']
        warnings1 = honeypotPayload['payload']['warnings']

        ownerDataPayload = requests.get('https://qpkjpvpeqx.us-east-1.awsapprunner.com/api/v1/contract-events/get-token-ownership-data/{}'.format(address)).json()
        devWalletHoldingPercentage = ownerDataPayload['payload']['ownershipData']['devWalletHoldingPercentage']
        isOwnershipRenounce = ownerDataPayload['payload']['ownershipData']['isOwnershipRenounce']

        otherDataPayload = requests.get('https://qpkjpvpeqx.us-east-1.awsapprunner.com/api/v1/contract-events/token-liquidity-data/{}'.format(address)).json()
        liquidityBnbAmount = otherDataPayload['payload']['liquidityBnbAmount']

        for warning in warnings1:
            if warning['type'] == 'success' and isOwnershipRenounce and devWalletHoldingPercentage <= 7 and float(liquidityBnbAmount) > 3:
                return [isHoneypot, MaxTxAmountBNB, BuyTax, SellTax]
        
        isHoneypot = True
        return [isHoneypot]

    def isHoneypot(tokenAddress):
        try:
            data = getTokenInfo(tokenAddress)
        except:
            return True

        if data[0] == True:
            return True

        else:
            if data[2] > 12 or data[3] > 12:
                return True
        return False

    def getRecentTokens():
        returnList = []
        tokens = requests.get('https://qpkjpvpeqx.us-east-1.awsapprunner.com/api/v1/contract-events/tokens?page=1&limit=10000&filter=created_at&direction=DESC').json()['payload']['items']

        for token in tokens:
            pattern = '%Y-%m-%dT%H:%M:%S.%fZ'

            tokenTime = token['createdAt']
            tokenEpochTime = int(time.mktime(time.strptime(tokenTime, pattern)))

            date_time = datetime.datetime.now()
            currentTime = date_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            currentEpochTime = int(time.mktime(time.strptime(currentTime, pattern)))

            threeHoursAgo = currentEpochTime - 21600          

            riskLevel = token['riskLevel']
            if riskLevel == None:
                risky = False
            else:
                if float(riskLevel) <= 40:
                    risky = False
                else:
                    risky = True


            if tokenEpochTime > threeHoursAgo and not risky and token['tokenAddress'] not in ['0x55d398326f99059ff775485246999027b3197955', '0x2170ed0880ac9a755fd29b2688956bd959f933f8']:
                returnList.append(token)
            else:
                if tokenEpochTime < threeHoursAgo:
                    break
        
        return returnList

    def filterScamTokens(tokenList):
        returnList = []
        for token in tokenList:
            if not isHoneypot(token['tokenAddress']):
                returnList.append(token)
        return returnList

        
    while True:
        try:
            portfolioTokenList = [] 
            for token in database.readAll('Portfolio'):
                portfolioTokenList.append(token[2])

            portfolioTokenList.append("0x772C4Fe1Fd65C590c1Fc92AfAd5A650ba43f0532")
                
            recentFilteredTokens = filterScamTokens(getRecentTokens())
            for token in recentFilteredTokens:
                print(web3.toChecksumAddress(token['tokenAddress']))
                
            for token in recentFilteredTokens:
                if  str(web3.toChecksumAddress(token['tokenAddress'])) not in portfolioTokenList:
                    rating = ''
                    checks = 0
                    while rating == "":
                        if checks < 5:
                            tokenRatingData = getTokenRating(token['tokenAddress'])
                            rating = tokenRatingData[0]
                            checks = checks + 1
                        else:
                            break

                    print("Rating: {}\n".format(rating))

                    if rating == '100/100' or rating == '95/100':
                        tokenName =  universalFunctions.getTokenData(token['tokenAddress'])[0]
                        if '2.0' not in tokenName and 'squid' not in str(tokenName).lower():
                            buyToken(Web3.toChecksumAddress(token['tokenAddress']), config.buyAmountBNB)
                else:
                    print('Already purchased...')
                time.sleep(3)
            
            time.sleep(60)
        except:
            pass
