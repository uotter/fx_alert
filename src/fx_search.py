import requests
import json

api_key = {"forge": "HRF2gjUR7Ewi94jrihzk9xNCY7Xlldiy", "currency": "29ef15d9477b19d44fd88221e48d1eb2"}
url_dic = {"forge": "https://forex.1forge.com/1.0.3/quotes?", "currency": "http://apilayer.net/api/live"}


def get_fx(api_name):
    url_base = url_dic[api_name]
    pairs = ",".join(codepairs)
    if api_name == "forge":
        data = {"api_key": api_key[api_name]}
    elif api_name == "currency":
        data = {"access_key": api_key[api_name]}
    else:
        raise NotImplementedError("Unknow api name.")
    # url = url_base+"pairs="+pairs+"&api_key="+api_key[api_name]
    # 执行请求
    response = requests.get(url_base, params=data)
    # 查看执行的url
    print('\n查看请求执行的url:\n', response.url)
    # 获得请求的内容
    print('\n获得请求的内容:\n', response.text)
    return response.text


def get_price_by_codepairs(codepairs, api_name):
    data = get_fx(api_name)
    price_dic = {}
    if api_name == "forge":
        price_dic = get_price_from_forge(codepairs, data)
    elif api_name == "currency":
        price_dic = get_price_from_currency(codepairs, data)
    else:
        raise NotImplementedError("Unknow api name.")
    return price_dic


def get_price_from_forge(codepairs, data):
    return_dic = {}
    json_data_list = json.loads(data)
    for json_data in json_data_list:
        if json_data["symbol"] in codepairs:
            return_dic[json_data["symbol"]] = json_data["price"]
    if len(set(codepairs) - set(return_dic.keys())) != 0:
        print("Not find the following code pairs:")
        print(",".join(list(set(codepairs) - set(return_dic.keys()))))
    return return_dic


def get_price_from_currency(codepairs, data):
    return_dic = {}
    json_data_dic = json.loads(data)["quotes"]
    for k, v in json_data_dic.items():
        if k in codepairs:
            return_dic[k] = v
    if len(set(codepairs) - set(return_dic.keys())) != 0:
        print("Not find the following code pairs:")
        print(",".join(list(set(codepairs) - set(return_dic.keys()))))
    return return_dic


if __name__ == "__main__":
    codepairs = ["USDBRL", "USDMXN"]
    api_names = ["currency", "forge"]
    for api_name in api_names:
        price_dic = get_price_by_codepairs(codepairs, api_name)
        print(api_name)
        for k, v in price_dic.items():
            print(k, ":", v)

