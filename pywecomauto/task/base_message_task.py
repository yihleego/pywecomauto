# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from urllib.parse import quote
from urllib.request import urlopen

from pywecomauto.task.base_task import *


class BaseMessageTask(BaseTask):

    def text_message(self, data):
        # 判断是否存在侧边栏 如果存在则等待一段时间
        if exists("sidebar_icon.png"):
            wait(3)
        # 点击消息输入框
        input_box_pos = exists("message_box.png")
        if input_box_pos:
            click((input_box_pos[0] + 50, input_box_pos[1] + 50), 0.5)
        # 清除输入框中可能存在的消息
        keyevent("^a{BACKSPACE}", 0.5)
        # 填写内容
        file_count = 0
        for content in data['contents']:
            type = content['type']
            # 当前企微发送文件限制一次性允许20个
            if file_count == 20:
                keyevent("{ENTER}", 1)
                file_count = 0
            if type == 'text':
                # 输入文本，判断文本长度是否超过4000，超过4000则切分
                if len(content['text']) <= 4000:
                    copy(content['text'])
                    keyevent("^v", 0.5)
                else:
                    texts = partition(content['text'], 4000)
                    for v in texts:
                        copy(v)
                        keyevent("^v", 0.5)
                        keyevent("{ENTER}", 1)
            elif type == 'img':
                # 选择图片
                click("select_image.png", 2)
                copy(content['path'])
                keyevent("^v", 0.5)
                keyevent("{ENTER}", 0.5)
                file_count = file_count + 1
            elif type == 'file':
                # 选择文件
                click("select_file.png", 2)
                copy(content['path'])
                keyevent("^v", 0.5)
                keyevent("{ENTER}", 0.5)
                file_count = file_count + 1
            elif type == 'mention':
                # 提醒用户
                if content['target']:
                    copy('@' + content['target'])
                    keyevent("^v", 0.5)
                    keyevent("{ENTER}", 0.5)
        keyevent("{ENTER}", 1)

    def download_files(self, data):
        dir = "{0}{1}".format(TEMP_PATH, datetime.now().strftime('%Y%m%d'))
        if not os.path.exists(dir):
            os.makedirs(dir)
        for content in data['contents']:
            if content.get('url') and content['type'] == 'img' or content['type'] == 'file':
                url = content['url']
                path = "{0}\\{1}".format(dir, os.path.basename(url))
                if os.path.exists(path):
                    content['path'] = path
                    logging.debug(f'文件已存在，跳过下载，url=\'{url}\'\npath=\'{path}\'')
                else:
                    response = urlopen(quote(url, safe='/:?='))
                    if response.getcode() == 200:
                        with open(path, "wb") as f:
                            f.write(response.read())
                            content['path'] = path
                            f.close()
