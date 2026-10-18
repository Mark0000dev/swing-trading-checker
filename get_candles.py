import pandas as pd
import requests
import hmac
import urllib.parse
from hashlib import sha256
import time
import os
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt
from define_atr import define_percentage_change
from list_of_tokens import LIST_OF_TOKENS
from configurator_swings import CONFIG

load_dotenv()
APIKEY = os.getenv('BING_SWING_API')
SECRETKEY = os.getenv('BING_SWING_SECRET')
APIURL = 'https://open-api.bingx.com'

input_url = '/openApi/swap/v3/quote/klines'
status_for_creating_charts = False

selected_interval = CONFIG['interval']
selected_timezone = CONFIG['timezone']
selected_limit = CONFIG['limit']
selected_time_interval = CONFIG['time_interval']

def load_request(token):
    payload = {}
    path = input_url
    method = "GET"
    paramsMap = {
        "symbol": token,
        "interval": selected_interval,
        'timezone': selected_timezone,
        "limit": selected_limit
}
    paramsStr, urlParamsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, urlParamsStr, payload)

def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    # print("sign=" + signature)
    return signature


def send_request(method, path, paramsStr, urlParamsStr, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlParamsStr, get_sign(SECRETKEY, paramsStr))
    # print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    response.raise_for_status()
    data = response.json()
    # print(data, ' RESPONSE')
    if data['code'] == 0:
        return response
    else:
        print(f'ошибка кода, сообщение: {data}')

def parseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsList = []
    urlParamsList = []
    for x in sortedKeys:
        value = paramsMap[x]
        paramsList.append("%s=%s" % (x, value))
    timestamp = str(int(time.time() * 1000))
    paramsStr = "&".join(paramsList)
    if paramsStr != "":
        paramsStr = paramsStr + "&timestamp=" + timestamp
    else:
        paramsStr = "timestamp=" + timestamp
    contains = '[' in paramsStr or '{' in paramsStr
    for x in sortedKeys:
        value = paramsMap[x]
        if contains:
            encodedValue = urllib.parse.quote(str(value), safe='')
            urlParamsList.append("%s=%s" % (x, encodedValue))
        else:
            urlParamsList.append("%s=%s" % (x, value))
    urlParamsStr = "&".join(urlParamsList)
    if urlParamsStr != "":
        urlParamsStr = urlParamsStr + "&timestamp=" + timestamp
    else:
        urlParamsStr = "timestamp=" + timestamp
    return paramsStr, urlParamsStr


if __name__ == '__main__':
    while True:
        for token in LIST_OF_TOKENS:
            response = load_request(token)
            if response is None:
                continue
            data = response.json()
            if data['code'] != 0:
                continue

            data_to_proceed = data['data']

            candles = []

            for row in data_to_proceed:
                candles.append({
                    'TimeStamp': pd.to_datetime(row['time'], unit='ms'),
                    'Open': float(row['open']),
                    'Close': float(row['close']),
                    'High': float(row['high']),
                    'Low': float(row['low'])
                })

            candles_df = pd.DataFrame(candles)
            define_percentage_change(candles_df, token)
            candles_df = candles_df.sort_values('TimeStamp')
            candles_df.to_csv(
                f'candles_df_{token}.csv',
                encoding='utf-8',
                index=False
            )
        time.sleep(selected_time_interval)

for token in LIST_OF_TOKENS:
    if status_for_creating_charts:
        file = (pd.read_csv(f'candles_df_{token}.csv'))
        plt.figure(figsize=(15, 6))
        plt.plot(file['TimeStamp'], file['Close'])
        plt.title(f'graph of {token}')
        plt.xticks(rotation=70)
        plt.show()