import sqlite3
import universalFunctions

conn = sqlite3.connect('db.db', check_same_thread=False)


def createPortfolioTable():
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Portfolio (indx INTEGER, transactionHash TEXT, tokenAddress TEXT, tokenName TEXT, buyPrice TEXT, estimatedSellPrice TEXT, date TEXT, transactions TEXT)')


def createTransactionsTable():
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Transactions (indx INTEGER, transactionHash TEXT, transactionType TEXT, tokenAddress TEXT, tokenName TEXT, estimatedTransactionPrice TEXT, transactionAmount TEXT, date TEXT)')


def readAll(tableName):
    c = conn.cursor()
    c.execute('SELECT * From {}'.format(tableName))
    data = c.fetchall()
    return data


def appendToPortfolio(transactionHash, tokenAddress, tokenName, buyPrice, estimatedSellPrice, date):
    index = len(readAll('Portfolio'))
    c = conn.cursor()
    c.execute("INSERT INTO Portfolio (indx, transactionHash, tokenAddress, tokenName, buyPrice, estimatedSellPrice, date, transactions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (index, transactionHash, tokenAddress, tokenName, buyPrice, estimatedSellPrice, date, 1))
    conn.commit()


def appendTransaction(transactionHash, transactionType, tokenAddress, tokenName, estimatedTransactionPrice, transactionAmount, date):
    index = len(readAll('Transactions'))
    c = conn.cursor()
    c.execute("INSERT INTO Transactions (indx, transactionHash, transactionType, tokenAddress, tokenName, estimatedTransactionPrice, transactionAmount, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (index, transactionHash, transactionType, tokenAddress, tokenName, estimatedTransactionPrice, str(transactionAmount), date,))
    conn.commit()


def read(tableName, identifierName, identifier):
    c = conn.cursor()
    c.execute('SELECT * From {} WHERE {}=(?)'.format(tableName, identifierName), (identifier,))
    data = c.fetchone()
    return data


def delete(tableName, identifierName, identifierValue):
    c = conn.cursor()
    c.execute('DELETE FROM {} WHERE {}=(?)'.format(tableName, identifierName), (identifierValue,))
    conn.commit()

def updatePortfolio(updateName, updateValue, identifierName, identifierValue):
    c = conn.cursor()
    c.execute('''UPDATE Portfolio SET {} = ? WHERE {} = ?'''.format(updateName, identifierName), (updateValue, identifierValue))
    conn.commit()


createPortfolioTable()
createTransactionsTable()
