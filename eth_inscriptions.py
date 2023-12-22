from curl_cffi import requests as cffi
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": "NEXT_LOCALE=en; __cuid=c963b9f0003b4e47a4a157c871819b96; amp_fef1e8=5f9213f9-42bd-4e0e-898e-30df1f070c0bR...1hhoal6jo.1hhobs8k8.1e.6.1k; cf_chl_2=1eccc0a4e66e96e; cf_clearance=T2VENdFl05djRMCt6i7neV9JWLM_5yilbLu0wLoD6qw-1702703933-0-1-6a841633.7e093fd.3d8549d3-160.0.0"
    }

if __name__ == '__main__':
    x1 = cffi.get('https://www.etch.market/api/markets/collections?category=token&tokenQuery=&page.size=10&page.index=1', impersonate="edge101", headers=headers)
    print(x1.text)