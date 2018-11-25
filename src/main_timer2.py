# -*- coding:utf-8 -*-

i
import datetime, configparser, sched, time, _datetime
from fx_search import ForeignExchange
from message import Email, Wechat

# 初始化sched模块的scheduler类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)

start_time = 0
end_time = 0


# def run_Task(api_name, codepairs):
#     email = Email()
#     fx = ForeignExchange()
#     result = fx.alert(api_name=api_name, codepairs=codepairs)
#     email.send_text(result)

def run_Task(api_name, codepairs):
    print("Exchange alert test.")


class mytimer():
    def __init__(self, exec_fun):
        # 被周期性调度触发的函数
        self.exec_function = exec_fun

    def cmd_timer(self, cmd, time_str, inc=60):
        # cmd：windows中命令行代码
        # time_str：哪一个时间点开始第一次执行
        # inc：两次执行的间隔时间
        # enter四个参数分别为：间隔时间、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，
        # 给该触发函数的参数（tuple形式）
        now = datetime.datetime.now()
        schedule_time = datetime.datetime.strptime(time_str, '%H:%M').replace(year=now.year, month=now.month,
                                                                              day=now.day)
        if schedule_time < now:
            schedule_time = schedule_time + datetime.timedelta(days=1)
        time_before_start = int(round((schedule_time - datetime.datetime.now()).total_seconds()))
        print(u'mytimer => 还有%s秒开始任务' % time_before_start)
        schedule.enter(time_before_start, 0, self.exec_function, (cmd, inc))
        schedule.run()


if __name__ == '__main__':
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
    print(u'exchange_alert => 第一次执行任务时间为%s,还有%s秒开始第一次任务' % (sched_Timer.strftime("%Y-%m-%d-%H-%M"), time_before_start))
    mytimer = mytimer(run_Task)
    mytimer.cmd_timer("netstat -an", '18:58', 10)
