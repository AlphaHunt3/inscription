from functools import lru_cache
from curl_cffi import requests
import json
from zenrows import ZenRowsClient
client = ZenRowsClient("7cb25caa7acba14279756160ab48b1d37be2491e")

UnisatAPIKey = "Bearer 2598ee096bfb6ea7af683a8264ff6d07277e3c79db12fc7756f68c6aa8f2caff"
CMCAPIKEY = "f06d7917-bad1-414a-bad7-692ace0af4e4"
inscriptions = {
    'btc':{
        'brc-20':['ordi','sats'],
        'arc-20':['atom','quark'],
        'lighting':['treat','trick','nostr'],
        'rune': ['cook','psbts'],
        'src-20': ['stamp']
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
        'erc-20': ['eths', 'Facet', 'gwei']
    },
    'mantle': {
        'mrc-20': ['mans']
    }
}

websites = {
    'ordi': 'https://www.coingecko.com/en/coins/ordi',
    'sats': 'https://www.coingecko.com/en/coins/sats-ordinals',
    'atom': 'https://atomicalmarket.com/market/token/atom',
    'quark': 'https://atomicalmarket.com/market/token/atom',
    'sols': 'https://www.coingecko.com/en/coins/sols',
    'pols': 'https://www.polsmarket.wtf/',
    'avav': 'https://avascriptions.com/market/token?tick=avav',
    'eths': 'https://www.etch.market/market/token?category=token&collectionName=erc-20%20eths',
    'Facet': 'https://www.etch.market/market/token?category=token&collectionName=erc-20%20Facet',
    'gwei': 'https://www.etch.market/market/token?category=token&collectionName=erc-20%20gwei',
    'treat': 'https://mainnet.nostrassets.com/#/marketplace/listing',
    'trick': 'https://mainnet.nostrassets.com/#/marketplace/listing',
    'nostr': 'https://mainnet.nostrassets.com/#/marketplace/listing',
    'mans': 'https://manbit.io/market/mans',
    'cook': 'https://runealpha.xyz/market',
    'psbts': 'https://runealpha.xyz/market',
    'stamp': 'https://openstamp.io/market/src20?tokenId=2&name=STAMP'
}


def get_token_price_coingecko(app_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={app_id}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    token_price = data[app_id]["usd"]
    return token_price


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


# def get_brc20_info(data_list):
#     btc_price = get_token_price("BTC")
#     sat_price = float(btc_price) / 1e8
#     for ticker in inscriptions['btc']['brc-20']:
#         headers = {
#             'Authorization': UnisatAPIKey,
#             'accept': 'application/json',
#             'Content-Type': 'application/json'
#         }
#         data = {
#             "timeType": "day1",
#             "tick": ticker
#         }
#         result = requests.post('https://open-api.unisat.io/v3/market/brc20/auction/brc20_types_specified',headers=headers,json=data).json()['data']
#         website = websites.get(ticker, "")
#         data_list.append([ticker,'btc','brc-20',result['curPrice']*sat_price,result['totalMinted']*result['curPrice']*sat_price,result['changePercent'],result['btcVolume']*sat_price, website])


def get_brc20_info_cmc(data_list):

    headers = {
        'X-CMC_PRO_API_KEY': CMCAPIKEY,
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    tokens = requests.get(f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?id=25028,28683',headers=headers).json()['data']
    for token in list(tokens.values()):
        ticker = token["slug"]
        metadata = token["quote"]["USD"]
        website = websites.get(ticker, "")
        data_list.append([ticker,'btc','brc-20',metadata["price"],metadata["market_cap"],metadata["percent_change_24h"],metadata["volume_24h"], website])


def get_sol_info(data_list):
    sol_price = get_token_price("SOL")
    for ticker in inscriptions['solana']['spl-20']:
        result = requests.get(f'https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{ticker}_spl20?status=all&edge_cache=true&agg=3', impersonate="chrome110").json()['results']
        supply = requests.get(f'https://api-mainnet.magiceden.io/rpc/getCollectionHolderStats/{ticker}_spl20?edge_cache=true', impersonate="chrome110").json()['results']['totalSupply']
        price = result['floorPrice']/1e9*sol_price
        website = websites.get(ticker, "")
        data_list.append([ticker,'solana','spl-20',result['floorPrice']/1e9*sol_price,supply*price,result['deltaFloor24hr']/(result['floorPrice']/1e9),result['volume24hr']/1e9*sol_price, website])


def get_polygon_info(data_list):
    matic_price = get_token_price("MATIC")
    for ticker in inscriptions['polygon']['prc-20']:
        params = {"js_render": "true", "autoparse":"true"}
        result = client.get(f'https://www.polsmarket.wtf/api-pols/markets/collections/details?category=token&collectionName=prc-20%20{ticker}', params=params).json()[0]['data']['collections']
        website = websites.get(ticker, "")
        data_list.append([ticker,'polygon','prc-20',float(result['floorPrice'])*matic_price,result['marketCap'],result['priceChangePercentage24h'] * 100,float(result['volume24h']) * matic_price, website])
    return data_list


def get_eth_info(data_list):
    eth_price = get_token_price("ETH")
    params = {"js_render": "true", "autoparse":"true"}
    result = client.get(f'https://www.etch.market/api/markets/collections?category=token&tokenQuery=&page.size=10&page.index=1', params=params).json()[0]['data']['collections'][:3]
    for token in result:
        ticker = token["collectionName"][7:]
        website = websites.get(ticker, "")
        data_list.append([ticker,'eth','erc-20',float(token['floorPrice'])*eth_price,token['marketCap'],token['priceChangePercentage24h'] * 100,float(token['volume24h'])*float(eth_price), website])
    return data_list


def get_avax_info(data_list):
    avax_price = get_avax_price()
    result = requests.post(f'https://avascriptions.com/api/order/market', impersonate="chrome110",json={"page": 1,"pageSize": 15,"keyword": ""}).json()['data']['list']
    dict = {}
    for i in result:
        dict[i['tick']] = i
    for ticker in inscriptions['avax']['asc-20']:
        mint_price = float(dict[ticker]['floorPrice'])/1e18*avax_price*dict[ticker]['perMint']
        price = float(dict[ticker]['floorPrice'])/1e18*avax_price
        website = websites.get(ticker, "")
        data_list.append([ticker,'avax','asc-20',mint_price,float(dict[ticker]['maxSupply'])*price,"N/A",float(dict[ticker]['volumeDay'])/1e9*price, website])


def get_arc20_info(data_list):
    btc_price = get_token_price("BTC")
    sat_price = float(btc_price) / 1e8
    headers = {
        "Referer": "https://atomicalmarket.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://atomicalmarket.com",
        "Accept": "application/json, text/plain, */*"
    }
    result = requests.get('https://server.atomicalmarket.com/market/v1/token-list', headers=headers).json()["data"]
    data = {}
    for item in result:
        data[item['name']] = item
    for ticker in inscriptions['btc']['arc-20']:
        website = websites.get(ticker, "")
        data_list.append([ticker,'btc','arc-20',data[ticker]['FloorPrice']*sat_price,data[ticker]['TotalSupply']*data[ticker]['FloorPrice']*sat_price,data[ticker]['Change'],data[ticker]['Volume24hour']*sat_price, website])


def get_nostr_info(data_list):
    btc_price = get_token_price("BTC")
    sat_price = float(btc_price) / 1e8
    result = requests.post('https://market-api.nostrassets.com/market/api/getTokenList').json()['data']
    dict = {}
    for i in result:
        dict[i['name'].lower()] = i
    for ticker in inscriptions['btc']['lighting']:
        website = websites.get(ticker, "")
        price = float(dict[ticker]['dealPrice'])/float(dict[ticker]['decimals'])
        data_list.append([ticker,'btc','lighting',price*sat_price,dict[ticker]['totalSupply']/float(dict[ticker]['decimals'])*price*sat_price,dict[ticker]['tfChange'],dict[ticker]['tfTotalPrice']*sat_price/float(dict[ticker]['decimals']), website])


def get_mantle_info(data_list):
    mnt_price = get_token_price_coingecko("mantle")
    for ticker in inscriptions['mantle']['mrc-20']:
        result = requests.get(
            f'https://api.manbit.xyz/mantles/tick?tick={ticker}',
            impersonate="chrome110").json()
        price = result['extend']['floor'] * mnt_price
        website = websites.get(ticker, "")
        data_list.append([ticker, 'mantle', 'mrc-20', price, result['tick']['amount'] * price, "N/A", "N/A", website])


def get_rune_info(data_list):
    btc_price = get_token_price("BTC")
    sat_price = float(btc_price) / 1e8
    headers = {
        "Referer": "https://runealpha.xyz",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://runealpha.xyz",
        "Accept": "application/json, text/plain, */*"
    }
    result = requests.get('https://api.runealpha.xyz/market/runes?limit=10&offset=0&sortBy=volume_24h&sortOrder=DESC', headers=headers).json()['data']
    dict = {}
    for i in result['runes']:
        dict[i['rune_name'].lower()] = i
    for ticker in inscriptions['btc']['rune']:
        website = websites.get(ticker, "")
        price = float(dict[ticker]['floor_price'])
        data_list.append([ticker,'btc','rune',price*sat_price,float(dict[ticker]['marketcap'])*sat_price,float(dict[ticker]['change_24h']),float(dict[ticker]['total_volume'])*sat_price, website])


def get_stamp_info(data_list):
    btc_price = get_token_price("BTC")
    sat_price = float(btc_price) / 1e8
    headers = {
        "Referer": "https://openstamp.io/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://openstamp.io/",
        "Accept": "application/json, text/plain, */*"
    }
    for ticker in inscriptions['btc']['src-20']:
        result = requests.get('https://openstamp.io/api/v1/src20/getMarketToken/2', headers=headers).json()['data']
        website = websites.get(ticker, "")
        data_list.append([ticker,'btc','src-20',float(result['price'])*sat_price,float(result['totalSupply'])*float(result['price'])*sat_price,float(result['change24'])*100,float(result['volume24'])*sat_price, website])


@lru_cache()
def get_all_data(_ts):
    data_list = []
    get_brc20_info_cmc(data_list)
    get_sol_info(data_list)
    get_polygon_info(data_list)
    get_avax_info(data_list)
    get_eth_info(data_list)
    get_nostr_info(data_list)
    get_arc20_info(data_list)
    get_mantle_info(data_list)
    get_rune_info(data_list)
    get_stamp_info(data_list)
    filter_data = []
    for i in data_list:
        filter_data.append({'tick':i[0],'blockchain':i[1],'protocol':i[2],'price':i[3],'fdv':i[4],'24h_change':i[5],'24h_volume':i[6],'website':i[7]})
    with open(f"./cache/inscriptions.json", "w") as output:
        json.dump(filter_data, output)
    return filter_data


if __name__ == "__main__":
    print(get_all_data(1))