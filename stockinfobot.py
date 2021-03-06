#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 14:49:21 2020

@author: kjaisingh
"""


# imports
import praw
import yfinance as yf
from extraction import tickers
import pandas as pd
import string
import os


# defining basic variables
reddit = praw.Reddit(client_id = os.environ.get('REDDIT_CLIENT_ID'),
                     client_secret = os.environ.get('REDDIT_CLIENT_SECRET'),
                     username = os.environ.get('REDDIT_USERNAME'),
                     password = os.environ.get('REDDIT_PASSWORD'),
                     user_agent = 'StockInfoBot by /u/kjaisingh')                 
subreddit = reddit.subreddit('Investing+Stocks')
key = '$$'


# check whether ticker is part of s&p 500 database
def isTicker(stock):
    return (stock in tickers)


# construct bot comment
def getTickerData(stock):
    
    # append basic bot output
    lines = []
    lines.append('Hello! This is the StockInfoBot created by /u/kjaisingh. I have come here to provide information about the ' + stock + ' stock.\n')
    
    # append basic stock data
    tickerInfo = yf.Ticker(stock)
    lines.append('Stock Name: ' + tickerInfo.info.get('shortName'))
    lines.append('Day Low: ' + '$' + str(tickerInfo.info.get('dayLow')) + '.')
    lines.append('Day High: ' + '$' + str(tickerInfo.info.get('dayHigh')) + '.')
    lines.append('Trading Volume: ' + str(tickerInfo.info.get('volume')) + '.')
    lines.append('50 Day Average: ' + '$' + str(tickerInfo.info.get('fiftyDayAverage')) + '.')
    lines.append('200 Day Average: ' + '$' + str(tickerInfo.info.get('twoHundredDayAverage')) + '.')
    lines.append('Company Industry: ' + tickerInfo.info.get('industry') + '.')
    lines.append('Company Website: ' + tickerInfo.info.get('website') + '.')
    
    # append stock recommendations if suitable number of recommendations available
    recommendations = tickerInfo.recommendations
    firms = recommendations.iloc[:, 0].values
    actions = recommendations.iloc[:, 1].values
    size = firms.size
    if(size > 10): 
        lines.append("Most Recent Analysis by Experts: " +
                     firms[size - 1] + " - " + actions[size - 1] + ", " +
                     firms[size - 2] + " - " + actions[size - 2] + ", " +
                     firms[size - 3] + " - " + actions[size - 3] + ", " +
                     firms[size - 4] + " - " + actions[size - 4] + ", " +
                     firms[size - 5] + " - " + actions[size - 5] + ".")
    
    # create a summary string with the comment data
    summary = ''
    for line in lines:
        summary += line
        summary += '\n\n'
        
    print(summary)
    
    # return string with comment data        
    return summary
    

# filter through each comment in stream
for comment in subreddit.stream.comments():
    
    # check if key is in comment body
    if key in comment.body:
        
        # separate words in comment
        text = comment.body
        words = text.split(" ")
        stocks = []
        
        # add ticker part of comment to list of tickers
        for word in words:
            if key in word:
                ticker = word.replace('$$', '')
                ticker.translate(str.maketrans('', '', string.punctuation))
                if ticker.isupper():
                    stocks.append(ticker)
        
        # try to construct and post comment for each ticker in comment
        try:
            for stock in stocks:
                if isTicker(stock):
                    reply = getTickerData(stock)
                    comment.reply(reply)
                    print('Information successfully posted for ' + stock + '.')
                else:
                    reply = stock + ' cannot be found on the S&P-500 index.'
                    comment.reply(reply)
                    print('Information unsuccessfully posted for ' + stock + '.')
        
        # print error message if failure occurs
        except:
            print('Hold your horses! Slow those requests down.')