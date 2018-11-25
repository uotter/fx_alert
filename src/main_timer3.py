import datetime
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
import datetime, os, platform, time, configparser
from fx_search import ForeignExchange
from message import Email, Wechat


def run_Task(api_name, codepairs):
    start_time = datetime.datetime.now()
    email = Email()
    fx = ForeignExchange()
    result = fx.alert(api_name=api_name, codepairs=codepairs)
    email.send_text(result)
    end_time = datetime.datetime.now()
    delay = round((end_time - start_time).total_seconds())
    print(u'[Info] exchange_alert => 开始时间：%s' % start_time)
    print(u'[Info] exchange_alert => 耗时:%s min' % (delay / 60))


def job_func(text):
    start_time = datetime.datetime.now()
    print("当前时间：", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    end_time = datetime.datetime.now()
    delay = round((end_time - start_time).total_seconds())
    print(u'[Info] exchange_alert => 开始时间：%s' % start_time)
    print(u'[Info] exchange_alert => 耗时:%s min' % (delay / 60))

if __name__ == "__main__":
    debug = False
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
                                    int(config.getint("alert", "start_hour")),
                                    int(config.getint("alert", "start_minute")), 00)
    time_before_start = int(round((sched_Timer - datetime.datetime.now()).total_seconds()))
    print(u'[Info] exchange_alert => 第一次执行任务时间为%s,还有%s秒开始第一次任务' % (sched_Timer.strftime("%Y-%m-%d-%H-%M"), time_before_start))
    scheduler = BlockingScheduler()  # 在每年 1-3、7-9 月份中的每个星期一、二中的 00:00, 01:00, 02:00 和 03:00 执行 job_func 任务
    start_hour = config.getint("alert", "start_hour")
    if debug:
        scheduler.add_job(job_func, 'cron', second=start_hour, args=['text'])
    else:
        scheduler.add_job(run_Task, 'cron', hour=start_hour, args=[api_name, codepairs])
    scheduler.start()
