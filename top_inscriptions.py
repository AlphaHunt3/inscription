from curl_cffi import requests
import json
import time
import base64
import hmac
import hashlib

UnisatAPIKey = "Bearer 2598ee096bfb6ea7af683a8264ff6d07277e3c79db12fc7756f68c6aa8f2caff"
inscriptions = {
    'btc':{
        'brc-20':['ordi','sats']
    },
    'solana':{
        'spl-20': ['sols']
    },
    'polygon':{
        'prc-20': ['pols']
    }
}


def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    btc_price = data["bitcoin"]["usd"]
    return btc_price


def get_solana_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    solana_price = data["solana"]["usd"]
    return solana_price


def get_matic_price():
    url = "https://www.okx.com/api/v5/public/mark-price?instType=SWAP&instId=MATIC-USDT-SWAP"
    response = requests.get(url)
    data = response.json()
    matic_price = data["data"][0]["markPx"]
    return float(matic_price)


def get_brc20_info(data_list):
    btc_price = get_btc_price()
    sat_price = float(btc_price) / 1e8
    for ticker in inscriptions['btc']['brc-20']:
        headers = {
            'Authorization': UnisatAPIKey,
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "timeType": "day1",
            "tick": ticker
        }
        result = requests.post('https://open-api.unisat.io/v3/market/brc20/auction/brc20_types_specified',headers=headers,json=data).json()['data']
        data_list.append([ticker,'btc','brc-20',result['curPrice']*sat_price,result['totalMinted']*result['curPrice']*sat_price,result['changePercent'],result['btcVolume']*sat_price])


def get_sol_info(data_list):
    sol_price = get_solana_price()
    for ticker in inscriptions['solana']['spl-20']:
        result = requests.get(f'https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{ticker}_spl20?status=all&edge_cache=true&agg=3', impersonate="chrome110").json()['results']
        supply = requests.get(f'https://api-mainnet.magiceden.io/rpc/getCollectionHolderStats/{ticker}_spl20?edge_cache=true', impersonate="chrome110").json()['results']['totalSupply']
        price = result['floorPrice']/1e9*sol_price
        data_list.append([ticker,'solana','spl-20',result['floorPrice']/1e9*sol_price,supply*price,result['deltaFloor24hr']/(result['floorPrice']/1e9),result['volume24hr']/1e9*sol_price])


def get_polygon_info(data_list):
    matic_price = get_matic_price()
    for ticker in inscriptions['polygon']['prc-20']:
        result = requests.get(f'https://www.polsmarket.wtf/api-pols/markets/collections/details?category=token&collectionName=prc-20%20{ticker}', impersonate="chrome110").json()['data']['collections']
        data_list.append([ticker,'polygon','prc-20',result['floorPrice']*matic_price,result['marketCap'],result['priceChangePercentage24h'],result['volume24h']])


def get_all_data():
    data_list = []
    get_brc20_info(data_list)
    get_sol_info(data_list)
    get_polygon_info(data_list)
    filter_data = []
    for i in data_list:
        filter_data.append({'tick':i[0],'blockchain':i[1],'protocol':i[2],'price':i[3],'fdv':i[4],'24h_change':i[5],'24h_volume':i[6]})
    with open(f"./cache/inscriptions_data.json", "w") as output:
        json.dump(filter_data, output)
    return filter_data


if __name__ == "__main__":
    print(get_all_data())