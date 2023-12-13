import requests
import json

UnisatAPIKey = "Bearer 2598ee096bfb6ea7af683a8264ff6d07277e3c79db12fc7756f68c6aa8f2caff"
inscriptions = {
    'btc':{
        'brc-20':['ordi','sats']
    }
}


def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    btc_price = data["bitcoin"]["usd"]
    return btc_price


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
        data_list.append([ticker,'btc','brc-20',result['curPrice']*sat_price,result['changePercent'],result['btcVolume']*sat_price])


def get_all_data():
    data_list = []
    get_brc20_info(data_list)
    with open(f"./cache/inscriptions_data.json", "w") as output:
        json.dump({"data":data_list}, output)
    return data_list


if __name__ == "__main__":
    print(get_all_data())