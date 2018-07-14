import smtplib
import email
import os
import logging
import sys
import click
from pathlib import Path
from datetime import datetime
from email.utils import formataddr
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.header import Header
from markdown2 import Markdown

@click.command()
@click.argument('target')
@click.option('--debug', type=click.BOOL, default=False, help='是否为DEBUG模式.')
def cli(target, debug):
    now = datetime.now()
    year = now.strftime('%Y')
    week = now.strftime('%U')
    file_path = os.getcwd() + f'/{year}年第{week}周-个人周报.md'
    with open(file_path, 'w+') as f:
        f.write("""
### 业务产出
### 技术产出
### 个人提升
        """)
        f.close()
    os.system(f'open {file_path}')
    flag = input('请问你编辑完成了么(yes/no)?\n')
    while flag != 'yes':
        flag = input(r'请问你编辑完成了么(yes/no)?\n')
    whisperer = Whisperer()
    whisperer.run(target, file_path, debug)
    click.echo('发送成功!')

class Whisperer():
    
    # smtp服务器地址
    smtp_server = 'smtp.mxhichina.com'
    # smtp端口
    smtp_port = 465
    # 自己的邮件
    my_email_address = None
    # 自己的密码
    my_email_password = None
    # 配置文件名
    config_name = '.whisperer.ini'
    # HOME目录
    workspace = str(Path.home()) + '/.whisperer'
    # 配置解析
    cfg = ConfigParser()
    # 是否处于DEBUG
    debug = False

    def prepare_setup(self):
        if self.debug is True:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        else:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
        name = self.config_name
        path = self.workspace + f'/{name}'
        if os.path.exists(path) is False:
            os.mkdir(self.workspace)
            self.my_email_address = input('请输入您的邮箱地址: ')
            self.my_email_password = input('请输入您的邮箱密码: ')
            self.cfg.add_section('base')
            self.cfg.set('base', 'my_email_address', self.my_email_address)
            self.cfg.set('base', 'my_email_password', self.my_email_password)
            with open(path, 'w+') as f:
                self.cfg.write(f)
        else:
            self.cfg.read(path)
            self.my_email_address = self.cfg.get('base', 'my_email_address')
            self.my_email_password = self.cfg.get('base', 'my_email_password')
        logging.info(f'当前的邮箱地址: {self.my_email_address}')
        logging.info(f'当前的邮箱密码: {self.my_email_password}')
    
    def build_email(self, html):
        message = MIMEText(html, 'html', 'utf-8')
        message['From'] = formataddr(['张斌辉', self.my_email_address])
        subject = '张斌辉 周报'
        message['Subject'] = Header(subject, 'utf-8')
        return message
    
    def build_email_from_markdown(self, path):
        html = None
        with open(path, 'r+') as f:
            content = f.read()
            marker = Markdown()
            html = marker.convert(content)
        return self.build_email(html)

    def send_email(self, to_address, message):
        server = smtplib.SMTP(self.smtp_server, timeout=10)
        server.set_debuglevel(self.debug)
        server.login(self.my_email_address, self.my_email_password)
        server.sendmail(self.my_email_address, [to_address], message.as_string())
        server.quit()

    def run(self, target, source, debug):
        self.debug = debug
        self.prepare_setup()
        email = self.build_email_from_markdown(source)
        self.send_email(target, email)