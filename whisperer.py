import smtplib
import email
import os
import logging
import sys
import click
import gitlab
import datetime
import re
from dateutil import parser
from dateutil.parser import parse
from datetime import datetime
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from email.utils import formataddr
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.header import Header
from markdown2 import Markdown

MY_GITLAB_HOST_KEY = "my_gitlab_host"
MY_GITLAB_PRIVATE_KEY = "my_gitlab_private_key"
MY_EMAIL_ADDRESS_KEY = "my_email_address"
MY_EMAIL_PASSWORD_KEY = "my_email_password"
MY_NICKNAME_KEY = "my_email_nickname"

@click.group()
def cli():
    pass

@cli.command()
def test():
    pass

@cli.command(help='配置邮箱服务器')
def server():
    pass

@cli.command(help='配置邮箱授权')
@click.argument('email', type=click.STRING)
@click.argument('password', type=click.STRING)
def auth(email, password):
    w = Whisperer()
    w.update_auth(email, password)
    click.echo('更新完成!')

@cli.command(help='配置Gitlab的Private-Key授权')
@click.argument('host', type=click.STRING)
@click.argument('key', type=click.STRING)
def auth_gitlab(host, key):
    w = Whisperer()
    w.update_private_key(host, key)
    click.echo('更新完成')

@cli.command(help='发送指定邮件')
@click.argument('target')
@click.option('--debug', type=click.BOOL, default=False, help='是否为DEBUG模式.')
def send(target, debug):
    whisperer = Whisperer()
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
    whisperer.append_commit_report(file_path)
    os.system(f'open {file_path}')
    md_prompet = '请问你编辑完成了么(YES or NO)?\n'
    flag = input(md_prompet)
    while flag.lower() != 'yes':
        flag = input(md_prompet)
    whisperer.run(target, file_path, debug)
    click.echo('发送成功!')

class Whisperer():
    
    # smtp服务器地址
    smtp_server = 'smtp.mxhichina.com'
    # smtp端口
    smtp_port = 465
    # gitlab域名
    my_gitlab_host = None
    # gitlab private key
    my_gitlab_private_key = None
    # 自己的邮件
    my_email_address = None
    # 自己的密码
    my_email_password = None
    # 发送邮件所用的昵称
    my_nickname = None
    # 配置文件名
    config_name = 'config.ini'
    # HOME目录
    workspace = str(Path.home()) + '/.whisperer'
    # 配置解析
    cfg = ConfigParser()
    # 是否处于DEBUG
    debug = False
    # 现在的时间
    now = datetime.now()
    # 过去一周开始的时间
    start_time = datetime.now() - timedelta(days=7)

    def __init__(self):
        self.prepare_setup()

    def prepare_setup(self):
        if self.debug is True:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        else:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
        name = self.config_name
        path = self.workspace + f'/{name}'
        if os.path.exists(path) is False:
            if not os.path.exists(self.workspace):
                os.mkdir(self.workspace)
            self.my_gitlab_host = input('请输入您gitlab的地址(例如https://git.souche-inc.com): ')
            self.my_gitlab_private_key = input('请输入您gitlab的Private-Key: ')
            self.my_email_address = input('请输入您的邮箱地址: ')
            self.my_email_password = input('请输入您的邮箱密码: ')
            self.my_nickname = input('请输入您的昵称(发送邮件所用): ')
            self.cfg.add_section('base')
            self.cfg.set('base', MY_GITLAB_HOST_KEY, self.my_gitlab_host)
            self.cfg.set('base', MY_GITLAB_PRIVATE_KEY, self.my_gitlab_private_key)
            self.cfg.set('base', MY_EMAIL_ADDRESS_KEY, self.my_email_address)
            self.cfg.set('base', MY_EMAIL_PASSWORD_KEY, self.my_email_password)
            self.cfg.set('base', MY_NICKNAME_KEY, self.my_nickname)
            with open(path, 'w+') as f:
                self.cfg.write(f)
        else:
            self.cfg.read(path)
            self.my_gitlab_host = self.cfg.get('base', MY_GITLAB_HOST_KEY)
            self.my_gitlab_private_key = self.cfg.get('base', MY_GITLAB_PRIVATE_KEY)
            self.my_email_address = self.cfg.get('base', MY_EMAIL_ADDRESS_KEY)
            self.my_email_password = self.cfg.get('base', MY_EMAIL_PASSWORD_KEY)
            self.my_nickname = self.cfg.get('base', MY_NICKNAME_KEY)
        logging.info(f'当前的gitlab域名: {self.my_gitlab_host}')
        logging.info(f'当前的邮箱地址: {self.my_email_address}')
        logging.info(f'当前的邮箱密码: {self.my_email_password}')

    def commit_from_lastweek(self):
        click.echo('正在链接gitlab服务...')
        gl = gitlab.Gitlab(self.my_gitlab_host, private_token=self.my_gitlab_private_key)
        gl.auth()
        start_year = self.start_time.strftime('%Y')
        start_month = self.start_time.strftime('%m')
        start_day = self.start_time.strftime('%d')
        click.echo(f'正在检索自从{start_year}年{start_month}月{start_day}日开始的事件...')
        events = gl.events.list(after=f'{start_year}-{start_month}-{start_day}')
        now = datetime.now()
        start = now - timedelta(days=7)
        all_commmits = []
        all_projectIds = set([])
        for item in events:
            all_projectIds.add(item.project_id)
        for project_id in all_projectIds:
            project = gl.projects.get(project_id, lazy=True)
            commits = project.commits.list(since=f'{start_year}-{start_month}-{start_day}T00:00:00Z')
            all_commmits += commits
        all_my_commit = list(filter(lambda x: x.author_email == self.my_email_address, all_commmits))
        all_my_commit.sort(key=lambda x:parser.parse(x.authored_date).date())
        return all_my_commit

    def append_commit_report(self, path):
        click.echo('正在追加检索本周所有的commit...')
        commits = self.commit_from_lastweek()
        commit_count = len(commits)
        code_line = 0
        commit_detail_array = []
        with open(path, 'a') as f:
            for commit in commits:
                time = parse(commit.authored_date).strftime('%x %X')
                msg = commit.message.splitlines()[0]
                commit_detail_array.append(f'| {commit.short_id}|{msg}|{time} |\n')
                for item_diff in commit.diff():
                    code_line += self.parser_diff_add_mode(item_diff["diff"])
            f.write('\n### Commit 统计 \n')
            f.write(f'本周共计产出 **{commit_count}** 个commit，贡献 **{code_line}** 行代码。 \n')
            f.write('\n---\n')
            f.write('\n| hash | message | date |\n')
            f.write('| --- | --- | --- |\n')
            for commit_detail in commit_detail_array:
                f.write(commit_detail)

    def update_auth(self, email, password):
        name = self.config_name
        path = self.workspace + f'/{name}'
        if os.path.exists(path) is False:
            os.mkdir(self.workspace)
            self.cfg.add_section('base')
        else:
            self.cfg.read(path)
        self.cfg.set('base', 'my_email_address', email)
        self.cfg.set('base', 'my_email_password', password)
        with open(path, 'w+') as f:
            self.cfg.write(f);

    def update_private_key(self, host, private_key):
        name = self.config_name
        path = self.workspace + f'/{name}'
        if os.path.exists(path) is False:
            os.mkdir(self.workspace)
            self.cfg.add_section('base')
        else:
            self.cfg.read(path)
        self.cfg.set('base', MY_GITLAB_HOST_KEY, host)
        self.cfg.set('base', MY_GITLAB_PRIVATE_KEY, private_key)
        with open(path, 'w+') as f:
            self.cfg.write(f);
        
    def build_email(self, html):
        nickname = self.my_nickname
        message = MIMEText(html, 'html', 'utf-8')
        message['From'] = formataddr([f'{nickname}', self.my_email_address])
        subject = f'{nickname} 周报'
        message['Subject'] = Header(subject, 'utf-8')
        return message
    
    def build_email_from_markdown(self, path):
        html = None
        with open(path, 'r+') as f:
            content = f.read()
            marker = Markdown(extras=["tables"])
            html = marker.convert(content)
        return self.build_email(html)

    def send_email(self, to_address, message):
        server = smtplib.SMTP(self.smtp_server, timeout=10)
        server.set_debuglevel(self.debug)
        server.login(self.my_email_address, self.my_email_password)
        server.sendmail(self.my_email_address, [to_address], message.as_string())
        server.quit()

    def parser_diff_add_mode(self, diff):
        lines = diff.split('\n')
        add_re = re.compile(r'^\+.+')
        add_line_number = 0
        for line in lines:
            if not re.match(add_re, line):
                add_line_number += 1
        return add_line_number

    def run(self, target, source, debug):
        self.debug = debug
        email = self.build_email_from_markdown(source)
        self.send_email(target, email)