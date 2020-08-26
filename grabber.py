import requests

def get_categories():
    url = "https://sapi.seeedstudio.com/fusion/opl/category?guid=59F77BC2E626DC07E4A497C34D387587&type=HQCHIP&appid=en.pc.bazaar"
    x = requests.post(url)
    rv = {}
    for item in x.json()['data']['list']:
        rv[item['category']] = {"count":item['count'], "download":False}
    return rv

def get_items(category):
    url = "https://sapi.seeedstudio.com/fusion/opl/list?guid=59F77BC2E626DC07E4A497C34D387587&appid=en.pc.bazaar"
    rv = []
    page = 0
    print(category, end="")
    while True:
        page += 1
        payload = {"page_offset":page,
           "page_length":30,
           "type":"HQCHIP",
           "keyword":"",
           "category":category,
           "advance":0
           }
        x = requests.post(url, data = payload)
        print(".", end="")
        if len(x.json()['data']['list']) == 0:
            break
        for item in x.json()['data']['list']:
            del item['ladder_price']
            rv.append(item)
    print()
    return rv
