<p align="center"> <img src="Project Elements/Binance_Smart_Chain_Arbitrage_Bot.png"/> </p>

<hr>
<br/>

```BSC MEV``` is a program that aimed to profit through the exploitation of block transaction fees.

## Use Case
Your first question is most likely "well why isn't everyone using this money printer?" frankly, it does not exactly work as intended. Due to funding limits, I had to work with coins that had a low market cap which would require roughly $500-1500 to move the price by 5%. This allowed me to profit with almost every trade I made but the issue with working with low market cap coins is their susceptibility to defective scam codes and rug pulls. On the other hand, larger coins that we verified often had participants with a faster system/network than myself, and dedicated chain nodes which led to me often losing bids. If I had more resources, I would improve this program by writing it entirely in solidity to allow me to reverse transactions if they don't close at my desired price and use a dedicated node to make my transactions faster. I did however absolutely love working on this project and it taught me a lot about Web3, different financial ideas, and of course the value of always being willing to learn something new.


## Installation

Use the package manager npm to install the following packages

```bash
pip install selenium
pip install web3
pip install pysqlite3
pip install requests
```

## Usage
This repo contains a buySide and a sellSide. The buy side monitors for new coins being created, scans the contract code to determine if it reaches the purchase criteria and finally buys. The sell side monitors the price change from when a coin was originally bought and determines if it has made enough profit to be sold.

```py
# Starting the buySide program
python3 buySide.py
```

```py
# Starting the sellSide program
python3 sellSide.py
```

I also included the concept code for the project written in JS because it is slightly faster and in the world of blockchain technology, even the smallest difference in speed could make the world of a difference.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
