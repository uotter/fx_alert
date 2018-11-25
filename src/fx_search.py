import requests
import json
import configparser
import time
import pandas as pd


class ForeignExchange():
    def __init__(self):
        self.debug = True
        self._init_config()

    def _init_config(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini", encoding="utf-8")
        self.config_sections = self.config.sections()

    def get_fx(self, api_name):
        url_base = self.config.get("baseurl", api_name)
        if api_name == "forge":
            data = {"api_key": self.config.get("token", api_name)}
        elif api_name == "currency":
            data = {"access_key": self.config.get("token", api_name)}
        else:
            raise NotImplementedError("Unknow api name.")
        # url = url_base+"pairs="+pairs+"&api_key="+api_key[api_name]
        # 执行请求
        response = requests.get(url_base, params=data)
        if self.debug:
            # 查看执行的url
            print('\n查看请求执行的url:\n', response.url)
            # 获得请求的内容
            print('\n获得请求的内容:\n', response.text)
        return response.text

    def get_price_by_codepairs(self, codepairs, api_name):
        data = self.get_fx(api_name)
        price_dic = {}
        if api_name == "forge":
            price_dic = self.get_price_from_forge(codepairs, data)
        elif api_name == "currency":
            price_dic = self.get_price_from_currency(codepairs, data)
        else:
            raise NotImplementedError("Unknow api name.")
        return price_dic

    def get_price_from_forge(self, codepairs, data):
        return_dic = {}
        json_data_list = json.loads(data)
        for json_data in json_data_list:
            if json_data["symbol"] in codepairs:
                return_dic[json_data["symbol"]] = json_data["price"]
        if len(set(codepairs) - set(return_dic.keys())) != 0:
            print("Not find the following code pairs:")
            print(",".join(list(set(codepairs) - set(return_dic.keys()))))
        return return_dic

    def get_price_from_currency(self, codepairs, data):
        return_dic = {}
        json_data_dic = json.loads(data)["quotes"]
        for k, v in json_data_dic.items():
            if k in codepairs:
                return_dic[k] = v
        if len(set(codepairs) - set(return_dic.keys())) != 0:
            print("Not find the following code pairs:")
            print(",".join(list(set(codepairs) - set(return_dic.keys()))))
        return return_dic

    def write_today_price(self, price_dic, api_name):
        time_str = time.strftime("%Y-%m-%d", time.localtime())
        with open(self.config.get("path", "history_data_path"), "a", encoding="utf-8") as f:
            for k, v in price_dic.items():
                f.write(time_str + "," + str(k) + "," + str(v) + "," + api_name + "\n")

    def alert(self, api_name, codepairs):
        return_str = ""
        today_time_str = time.strftime("%Y-%m-%d", time.localtime())
        today_price_dic = self.get_price_by_codepairs(codepairs, api_name)
        his_df = pd.read_csv(self.config.get("path", "history_data_path"), header=None, encoding="utf-8")
        his_df.columns = ["date", "pair", "price", "source"]
        his_df.sort_values("date")
        for codepair in codepairs:
            last_price = -1
            for idx in reversed(his_df.index):
                if his_df.loc[idx, 'pair'] == codepair and his_df.loc[idx, 'source'] == api_name:
                    last_price = his_df.loc[idx, 'price']
                    break
            if last_price == -1:
                return_str += "Cannot find previous price for " + codepair + " on " + today_time_str + ".\n"
            elif codepair not in today_price_dic.keys():
                return_str += "Cannot find today price for " + codepair + " on " + today_time_str + ".\n"
            else:
                today_price = today_price_dic[codepair]
                change_rate = (float(today_price) - float(last_price)) / float(last_price)
                if abs(change_rate) > self.config.getfloat("alert", "threshold"):
                    return_str += "!!![Warning] Price change for " + codepair + " on " + today_time_str + " with %.4f percent !!!\n" % (
                            change_rate * 100)
                else:
                    return_str += "Price change for " + codepair + " on " + today_time_str + " with %.4f percent.\n" % (
                            change_rate * 100)
                return_str += "last price %.4f, today_price %.4f for %s\n" % (last_price, today_price, codepair)
            return_str += "\n"
        self.write_today_price(today_price_dic, api_name)
        return return_str


if __name__ == "__main__":
    codepairs = ["USDBRL", "USDMXN"]
    api_names = ["currency", "forge"]
    forgine_exchage = ForeignExchange()
    result = forgine_exchage.alert(api_names[0], codepairs)
    print(result)
