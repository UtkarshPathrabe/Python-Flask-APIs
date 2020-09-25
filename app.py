from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from csv import reader
from bisect import bisect_left
from collections import defaultdict

app = Flask(__name__)
app.config['DEBUG'] = True

def readTransactionDataFromCSV(fileName):
    data = {}
    with open(fileName) as csvFile:
        csvReader = reader(csvFile)
        lineCount = 0
        header = []
        for row in csvReader:
            if lineCount == 0:
                header = row
                lineCount += 1
            else:
                transactionId = 0
                rowData = {}
                for index, element in enumerate(row):
                    if index == 0:
                        transactionId = int(str(element).strip())
                        rowData[str(header[index]).strip()] = transactionId
                    elif index == 1:
                        rowData[str(header[index]).strip()] = int(str(element).strip())
                    elif index == 2:
                        rowData[str(header[index]).strip()] = float(str(element).strip())
                    elif index == 3:
                        rowData[str(header[index]).strip()] = datetime.fromisoformat(str(element).strip())
                data[transactionId] = rowData
                lineCount += 1
        app.logger.info('Read {} lines from {}'.format(lineCount, fileName))
    return data

transactions = readTransactionDataFromCSV('transactions.csv')

transactionsSummarySortedByDatetime = sorted(transactions.values(), key = lambda x : x['transactionDatetime'])

def readProductReferenceDataFromCSV(fileName):
    data = {}
    with open(fileName) as csvFile:
        csvReader = reader(csvFile)
        lineCount = 0
        header = []
        for row in csvReader:
            if lineCount == 0:
                header = row
                lineCount += 1
            else:
                productId = 0
                rowData = {}
                for index, element in enumerate(row):
                    if index == 0:
                        productId = int(str(element).strip())
                    elif index == 1:
                        rowData[str(header[index]).strip()] = str(element).strip()
                    elif index == 2:
                        rowData[str(header[index]).strip()] = str(element).strip()
                data[productId] = rowData
                lineCount += 1
        app.logger.info('Read {} lines from {}'.format(lineCount, fileName))
    return data

products = readProductReferenceDataFromCSV('ProductReference.csv')

@app.route('/', methods = ['GET'])
def home():
    return '<h1>Transaction Retrieval</h1><p>This provides prototype APIs for retrieving transaction data and its various summaries.</p>'

@app.route('/assignment/transaction/<transactionId>', methods = ['GET'])
def getTransactionDetails(transactionId):
    if not transactionId:
        return '<p>Error: Transaction ID not provided. Please provide Transaction ID.</p>'
    transactionId = int(transactionId)
    if transactionId in transactions:
        transactionDetails = transactions[transactionId]
        return jsonify(transactionDetails)
    else:
        return '<p>Error: Invalid Transaction ID.</p>'

@app.route('/assignment/transactionSummaryByProducts/<n>', methods = ['GET'])
def getTransactionSummaryByProducts(n):
    if not n:
        return '<p>Error: Proper parameter not provided. Please provide the last number of days value for which you want the summary.</p>'
    n = int(n)
    validDate = datetime.now() - timedelta(days = n)
    app.logger.info('Fetching Summary of Transactions from {}'.format(validDate))
    keys = [data['transactionDatetime'] for data in transactionsSummarySortedByDatetime]
    startIndex = bisect_left(keys, validDate)
    summaryMap = defaultdict(float)
    for index in range(startIndex, len(transactionsSummarySortedByDatetime)):
        summaryMap[products[transactionsSummarySortedByDatetime[index]['productId']]['productName']] += transactionsSummarySortedByDatetime[index]['transactionAmount']
    summary = []
    for productName, totalAmount in summaryMap.items():
        summary.append({'productName': productName, 'totalAmount': totalAmount})
    return jsonify({'summary': summary})

@app.route('/assignment/transactionSummaryByManufacturingCity/<n>', methods = ['GET'])
def getTransactionSummaryByManufacturingCity(n):
    if not n:
        return '<p>Error: Proper parameter not provided. Please provide the last number of days value for which you want the summary.</p>'
    n = int(n)
    validDate = datetime.now() - timedelta(days = n)
    app.logger.info('Fetching Summary of Transactions from {}'.format(validDate))
    keys = [data['transactionDatetime'] for data in transactionsSummarySortedByDatetime]
    startIndex = bisect_left(keys, validDate)
    summaryMap = defaultdict(float)
    for index in range(startIndex, len(transactionsSummarySortedByDatetime)):
        summaryMap[products[transactionsSummarySortedByDatetime[index]['productId']]['productManufacturingCity']] += transactionsSummarySortedByDatetime[index]['transactionAmount']
    summary = []
    for cityName, totalAmount in summaryMap.items():
        summary.append({'cityName': cityName, 'totalAmount': totalAmount})
    return jsonify({'summary': summary})

@app.errorhandler(404)
def page_not_found(e):
    return '<h1>Not Found</h1><p>The resource could not be found.</p>', 404

app.run()