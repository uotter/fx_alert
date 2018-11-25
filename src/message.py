# 导入模块
import datetime

from wxpy import *
import smtplib
from email.mime.text import MIMEText
import configparser


class Wechat():
    def __init__(self):
        self._init_bot()
        self.target = None

    def _init_bot(self):
        self.bot = Bot()

    def set_target(self, friend_name):
        self.target = self.bot.friends.search(friend_name)

    def send_text(self, text):
        if self.target is None:
            raise NameError("No send target.")
        else:
            self.target.send(text)

    def send_image(self, image_path):
        if self.target is None:
            raise NameError("No send target.")
        else:
            self.target.send_image(image_path)


class Email():
    def __init__(self):
        self._init_config()
        self.mail_host = self.config.get("email", "mail_host")
        self.mail_user = self.config.get("email", "mail_user")
        self.mail_pass = self.config.get("email", "mail_pass")
        self.sender = self.config.get("email", "sender")
        self.receivers = self.config.get("email", "receivers").split(",")

    def _init_config(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini", encoding="utf-8")
        self.config_sections = self.config.sections()

    def send_text(self, text):
        # 邮件内容设置
        self.message = MIMEText(text, 'plain', 'utf-8')
        # 邮件主题
        if "Warning" in text:
            self.message['Subject'] = '[Warning]Exchange Alert on %s' % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        else:
            self.message['Subject'] = 'Exchange Alert on %s' % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # 发送方信息
        self.message['From'] = self.sender
        # 接受方信息
        self.message['To'] = self.receivers[0]
        # 登录并发送邮件
        try:
            smtpObj = smtplib.SMTP()
            # 连接到服务器
            smtpObj.connect(self.mail_host, 25)
            # 登录到服务器
            smtpObj.login(self.mail_user, self.mail_pass)
            # 发送
            smtpObj.sendmail(
                self.sender, self.receivers, self.message.as_string())
            # 退出
            smtpObj.quit()
            print('success')
        except smtplib.SMTPException as e:
            print('error', e)  # 打印错误


if __name__ == "__main__":
    email = Email()
    email.send_text("test")
