import datetime, os, platform, time, configparser
import pandas as pd
import numpy as np
from fx_search import ForeignExchange
from message import Email, Wechat


def run_Task(api_name, codepairs):
    email = Email()
    fx = ForeignExchange()
    result = fx.alert(api_name=api_name, codepairs=codepairs)
    email.send_text(result)


# def run_Task(api_name, codepairs):
#     print("Exchange alert test.")


def timeFun(sched_Timer, api_name, codepairs, delta_value, delta_type):
    flag = 0
    while True:
        now = datetime.datetime.now()
        # print(now.strftime("%Y-%m-%d-%H-%M-%S"),sched_Timer.strftime("%Y-%m-%d-%H-%M-%S"),now == sched_Timer)
        if now.strftime("%Y-%m-%d-%H-%M-%S") == sched_Timer.strftime("%Y-%m-%d-%H-%M-%S") and flag == 0:
            start_time = datetime.datetime.now()
            run_Task(api_name, codepairs)
            end_time = datetime.datetime.now()
            delay = round((end_time - start_time).total_seconds())
            print(u'exchange_alert => 开始时间：%s' % start_time)
            print(u'exchange_alert => 耗时:%s min' % (delay / 60))
            flag = 1
        else:
            if flag == 1:
                if delta_type == "minute":
                    sched_Timer = sched_Timer + datetime.timedelta(minutes=delta_value)
                elif delta_type == "day":
                    sched_Timer = sched_Timer + datetime.timedelta(days=delta_value)
                elif delta_type == "hour":
                    sched_Timer = sched_Timer + datetime.timedelta(hours=delta_value)
                elif delta_type == "second":
                    sched_Timer = sched_Timer + datetime.timedelta(seconds=delta_value)
                else:
                    raise NotImplementedError("Unknown delta_type %s" % delta_type)
                flag = 0
                print(u'exchange_alert => 下次执行:%s' % (sched_Timer.strftime("%Y-%m-%d-%H-%M-%S")))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    api_name = config.get("alert", "apiname")
    codepairs = config.get("alert", "codepairs").split(",")
    delta_value = config.getint("alert", "delta_value")
    delta_type = config.get("alert", "delta_type")
    today_time_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M").split("-")
    # today_time_str[3] is the hour
    if int(today_time_str[3]) >= config.getint("alert", "start_hour"):
        first_time_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d-%H-%M").split("-")
    else:
        first_time_str = today_time_str
    sched_Timer = datetime.datetime(int(first_time_str[0]), int(first_time_str[1]), int(first_time_str[2]),
                                    int(config.getint("alert", "start_hour")), int(config.getint("alert", "start_minute")), 00)
    time_before_start = int(round((sched_Timer - datetime.datetime.now()).total_seconds()))
    print(u'exchange_alert => 第一次执行任务时间为%s,还有%s秒开始第一次任务' % (sched_Timer.strftime("%Y-%m-%d-%H-%M"), time_before_start))
    timeFun(sched_Timer, api_name, codepairs, delta_value, delta_type)
    # run_Task(api_name, codepairs)
