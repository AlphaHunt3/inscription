from functools import lru_cache
from curl_cffi import requests
import json
from zenrows import ZenRowsClient
client = ZenRowsClient("da90810786dd26f038fda4a9929a0ee603573eb2")

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
    },
    'avax':{
        'asc-20': ['avav']
    },
    'eth':{
        'erc-20': ['eths', 'Facet']
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


def get_token_price(tick):
    url = f"https://www.okx.com/api/v5/public/mark-price?instType=SWAP&instId={tick}-USDT-SWAP"
    response = requests.get(url)
    data = response.json()
    token_price = data["data"][0]["markPx"]
    return float(token_price)


def get_avax_price():
    url = "https://www.okx.com/api/v5/public/mark-price?instType=SWAP&instId=AVAX-USDT-SWAP"
    response = requests.get(url)
    data = response.json()
    avax_price = data["data"][0]["markPx"]
    return float(avax_price)


def get_brc20_info(data_list):
    btc_price = get_token_price("BTC")
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
    sol_price = get_token_price("SOL")
    for ticker in inscriptions['solana']['spl-20']:
        result = requests.get(f'https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{ticker}_spl20?status=all&edge_cache=true&agg=3', impersonate="chrome110").json()['results']
        supply = requests.get(f'https://api-mainnet.magiceden.io/rpc/getCollectionHolderStats/{ticker}_spl20?edge_cache=true', impersonate="chrome110").json()['results']['totalSupply']
        price = result['floorPrice']/1e9*sol_price
        data_list.append([ticker,'solana','spl-20',result['floorPrice']/1e9*sol_price,supply*price,result['deltaFloor24hr']/(result['floorPrice']/1e9),result['volume24hr']/1e9*sol_price])


def get_polygon_info(data_list):
    matic_price = get_token_price("MATIC")
    for ticker in inscriptions['polygon']['prc-20']:
        params = {"js_render": "true", "autoparse":"true"}
        result = client.get(f'https://www.polsmarket.wtf/api-pols/markets/collections/details?category=token&collectionName=prc-20%20{ticker}', params=params).json()[0]['data']['collections']
        data_list.append([ticker,'polygon','prc-20',float(result['floorPrice'])*matic_price,result['marketCap'],result['priceChangePercentage24h'],result['volume24h']])
    return data_list


def get_eth_info(data_list):
    eth_price = get_token_price("ETH")
    params = {"js_render": "true", "autoparse":"true"}
    result = client.get(f'https://www.etch.market/api/markets/collections?category=token&tokenQuery=&page.size=10&page.index=1', params=params).json()[0]['data']['collections'][:3]
    for token in result:
        ticker = token["collectionName"][7:]
        data_list.append([ticker,'eth','erc-20',float(token['floorPrice'])*eth_price,token['marketCap'],token['priceChangePercentage24h'],token['volume24h']])
    return data_list

def get_avax_info(data_list):
    avax_price = get_avax_price()
    result = requests.post(f'https://avascriptions.com/api/order/market', impersonate="chrome110",json={"page": 1,"pageSize": 15,"keyword": ""}).json()['data']['list']
    dict = {}
    for i in result:
        dict[i['tick']] = i
    for ticker in inscriptions['avax']['asc-20']:
        price = float(dict[ticker]['floorPrice'])/1e18*avax_price*dict[ticker]['perMint']
        data_list.append([ticker,'avax','asc-20',price,float(dict[ticker]['maxSupply'])/1e9*price,0,float(dict[ticker]['volumeDay'])/1e9*price])


@lru_cache()
def get_all_data(_ts):
    data_list = []
    get_brc20_info(data_list)
    get_sol_info(data_list)
    get_polygon_info(data_list)
    get_avax_info(data_list)
    get_eth_info(data_list)
    filter_data = []
    for i in data_list:
        filter_data.append({'tick':i[0],'blockchain':i[1],'protocol':i[2],'price':i[3],'fdv':i[4],'24h_change':i[5],'24h_volume':i[6]})
    with open(f"./cache/inscriptions.json", "w") as output:
        json.dump(filter_data, output)
    return filter_data


if __name__ == "__main__":
    print(get_all_data())