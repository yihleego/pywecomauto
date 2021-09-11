# -*- coding: utf-8 -*-
import base64
import json
import re
import unittest

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from airtest.core.api import connect_device
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import find_window
from win32gui import SetWindowText

from pywecomauto.common.rsa_sign import sign_sha256_with_rsa
from pywecomauto.openapi.service import to_sign_content
from pywecomauto.rpa.task.base_task import click
from pywecomauto.rpa.task.client_check_task import ClientCheckTask
from pywecomauto.rpa.task.login_task import LoginTask


def clear_dict(d):
    if d is None:
        return None
    elif isinstance(d, list):
        return list(filter(lambda x: x is not None, map(clear_dict, d)))
    elif not isinstance(d, dict):
        return d
    else:
        r = dict(
            filter(lambda x: x[1] is not None,
                   map(lambda x: (x[0], clear_dict(x[1])),
                       d.items())))
        if not bool(r):
            return None
        return r


class TaskTestSuite(unittest.TestCase):
    def test_qrcode_task(self):
        task = LoginTask()
        url1 = task.run(0x411190)
        print(url1)
        assert url1 is not None

    def test_login_task(self):
        task = ClientCheckTask()
        task.run(0x5A311E)
        assert True

    def test_userinfo(self):
        title = 'WeCom|BLACK|Spot|叶伟|毅|10_4'
        values = re.findall("\\|(\\d+)_(\\d+)$", title[title.rindex("|"):])
        p = '^WeCom\\|(.{%s})\\|(.{%s})' % values[0]
        values = re.findall(p, title)
        print(values)
        SetWindowText(0x200BF6, '企业微信')

    def test_menu(self):
        dev = connect_device("Windows:///" + str(0x200BF6))
        dev.set_foreground()
        dev.move((0, 0))
        click(['more_menu.png', 'more_menu2.png'], 1)
        menu_handle = find_window(class_name="DuiMenuWnd")
        win = HwndWrapper(menu_handle)
        menu_dev = connect_device("Windows:///" + str(menu_handle))
        settings_pos = click(r"settings.png")

        # dev2 = connect_device("Windows:///" + str(menu_handle))
        print(1)

    def test_sign(self):
        b_private_key = 'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCdb8eqCj+8bhRp1Nczsn11zbwv/yWuZI5U6A2kofCzeFluFT7vA0MEgQfXCr+K7nJAH940WowQz16QcCygBsI/HNvS8cvnNJUH41sp7knq03Lse4b8TbrclFQeG8isJQgP8jVSz7fXoIwZeZee8SROn7iwz6gJtAqugfHvAK1IjXM6ZtmaaZcnUYT1K/imkZ91ayu5w6yLt1MwW+aqREVWb+49ZYDzfCFuOfUH7wNYnMkiRN1qwLojhXrVlRn/QRyAXmbisfHm40q0bFw9tv/TPvNLssiqi4iwO2Obub/lM25lZ9qOcyqWEHr9xATQdhQs6eYtzxNBohXbjjyKJ7K3AgMBAAECggEAAfVx2KsSXObvhR2Qcxo+aENsN+Cn/J7cHM3fNp1y/Pu9aBJpujLYB3w4Q+Fog9Y43Zz9kSx5rhmrCdG44x+GBGXoIf91HgcilLSC5lbAR/k+vUh7hOmUFcHGK0+JP5g2OcH73NMolfqxej+IrmUEcRvKRC3MlWMYvgW6YeusM/7EozZgF4pzoiy15OU/MFYD6QIaPCcWZmpFkBXz0JQijUzrDu+y6t1N0SzJokX9X4rbqLKPO3UPJZIhCJ4WkVlP/p54BT+AMgExyUfdD1q1H6ZrqNbREmH76K1ebviorNLouqzy5Vr73JedM6wNFeid0aD0XXWOCjHVK8H3DU5FCQKBgQDDITargdKJColTjl6wU7uIhEQ7dXctbWiyfswUi3wb3CeA7tKSQnsZTYDfFc6wMEnNxPhbTzb/Q0cUI7PUdxLEZIQSIVl2+13pqV6qKm8PYBstcIHtaNaB05pgfSknyITqG9DMntIOuBp1ltueTDraMn8lYOD5g9TV/+RAa5z2EwKBgQDOjHLObMioLAxH3f315yodCquOcYT3vAI12tKar6pdlxc0Z3FnmjKYiATSD3P1qbRzAHCDqXfrAgjbsx4plXc8xnEIxjxZBpJMABgCl/zK/xEHyZ8dgCr8FLCvhOW3wv/CpzDbm1KpahTanQhEhSKXERK22L50Zyh3js1Ubfl1TQKBgBNL6I0jZH+a5CO4M5L6ZNRGSD0dC7EZXb4xHdt2Q8q5hcqRU4+VNXk2GeV10Z/I1rObo/fbqJOrwo6yTSlYsSlsy0bDt4Y1q37c+fiYA62gkm927dJdiMED/QNHvVcq1EIWiBqEJj/AYxV32rYX0cYcMkivAPCL4fNbv+XC/p2zAoGAIp1I9C0o534SRM0ALYCi/yD1pTaDCR1Z5XqZhtDfpTWX7vFTAQDHb+aDoEx0q3vYQNmXAYmaDilWILOA34kr5WSANu8519WRGOl/HJgqBj7+tKZmYwRCr+Irxg5ojQZB5HYuau85yCh9/DEK3KjPJi/3SetC57EOCBNHd9nCT5UCgYEAghMoFFzoPgdNPwz5Y+jW8kYtRPDCj9BZTBrvFZp13vR79oDrfDTSvRa5VmDy0qIhHHM9Ydr2QpO01jFwjUk8AnTTariK/p0JcA1ElDX4Q1jdEqP1ncJsiI73qk+k30WW9Uu/ZCmUFDyYIWuVgMjesUUDspQy/dpqQgdJRgkWBQQ='
        b_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnW/Hqgo/vG4UadTXM7J9dc28L/8lrmSOVOgNpKHws3hZbhU+7wNDBIEH1wq/iu5yQB/eNFqMEM9ekHAsoAbCPxzb0vHL5zSVB+NbKe5J6tNy7HuG/E263JRUHhvIrCUID/I1Us+316CMGXmXnvEkTp+4sM+oCbQKroHx7wCtSI1zOmbZmmmXJ1GE9Sv4ppGfdWsrucOsi7dTMFvmqkRFVm/uPWWA83whbjn1B+8DWJzJIkTdasC6I4V61ZUZ/0EcgF5m4rHx5uNKtGxcPbb/0z7zS7LIqouIsDtjm7m/5TNuZWfajnMqlhB6/cQE0HYULOnmLc8TQaIV2448iieytwIDAQAB'
        # 以下是签名部分
        # 要签名的内容
        data = b'123456'
        # 获取要签名的内容的HASH值。摘要算法是什么不重要，只要验证时使用一样的摘要算法即可
        digest = SHA256.new(data)
        # 读取私钥
        private_key = RSA.import_key(base64.b64decode(b_private_key))
        # 对HASH值使用私钥进行签名。所谓签名，本质就是使用私钥对HASH值进行加密
        signature = pkcs1_15.new(private_key).sign(digest)
        print(str(base64.b64encode(signature)))
        # 以下是签名校验部分
        # 签名部分要传给签名校验部分三个信息：签名内容原文、摘要算法、HASH值签名结果
        # 获取被签名的内容的HASH值。使用与签名部分一样的摘要算法计算
        digest = SHA256.new(data)
        # 读取公钥
        public_key = RSA.import_key(base64.b64decode(b_public_key))
        try:
            # 进行签名校验。本质上就是使用公钥解密signature，看解密出来的值是否与digest相等
            # 相等则校验通过，说明确实data确实原先的内容；不等则校验不通过，data或signature被篡改
            # 可能有人会想，如果我先修改data然后再用自己的私钥算出signature，是不是可以完成欺骗？
            # 答案是不能，因为此时使用原先的公钥去解signature，其结果不会等于digest
            pkcs1_15.new(public_key).verify(digest, signature)
            print(f"The signature is valid.")
        except (ValueError, TypeError):
            print("The signature is not valid.")

    def test_json_to_str(self):
        data = [
            {
                "scheduled_time": "2021-08-06 15:15:27",
                "type": 3,
                "content": {
                    "messages": [
                        {
                            "recipient": "user1",
                            "contents": [
                                {
                                    "type": "0",
                                    "value": "hello"
                                }
                            ]
                        },
                        {
                            "recipient": "user2",
                            "contents": [
                                {
                                    "type": "0",
                                    "value": "hello"
                                }
                            ]
                        }
                    ]
                },
                "company_name": "人之初教育",
                "user_name": "YeWeiYi"
            }
        ]
        print(json.dumps(data, sort_keys=True, ensure_ascii=False).replace("\"", "\\\""))

    def test_s(self):
        s = to_sign_content({
            "app_id": 1,
            "method": "task.create",
            "timestamp": "1631175056105",
            "signature": "fLGhIAd8EHxR/jyXzKfqDN/zi/lvwq3dfn9Enqyix0YoyGIQoVxj6wd9cSpE4r8eyRRlUdHPYxuyMGaxTb6tf7scBxFXLzVORkbvZ0W3lKsCvuu4jmuWYfZPI4q1OwRI82ZqWscwSTViCwl50hRtUnCNX0Y3qM9EsgQG6hpbeNDzFCJqZzrlRIdEAsbHY04wVXYKuT0mNa4HxlA2p1oT2bjbJVJPnYhwGHtV+rKs5QW35Gyu1ElLedKLsHWKChucuBP0FgF/DTtLEeKNLWKgsQO7cuItDCu5PGc/cMUrV/OUqcl4fWGPRZ6qXpqFIHDH2vzGMCmHalg1TiUc+d3Kmw==",
            "content": "[{\"company_name\": \"人之初教育\", \"content\": {\"messages\": [{\"contents\": [{\"type\": \"0\", \"value\": \"hello\"}], \"recipient\": \"user1\"}, {\"contents\": [{\"type\": \"0\", \"value\": \"hello\"}], \"recipient\": \"user2\"}]}, \"scheduled_time\": \"2021-08-06 15:15:27\", \"type\": 3, \"user_name\": \"YeWeiYi\"}]"
        })
        sign = sign_sha256_with_rsa(
            'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCdb8eqCj+8bhRp1Nczsn11zbwv/yWuZI5U6A2kofCzeFluFT7vA0MEgQfXCr+K7nJAH940WowQz16QcCygBsI/HNvS8cvnNJUH41sp7knq03Lse4b8TbrclFQeG8isJQgP8jVSz7fXoIwZeZee8SROn7iwz6gJtAqugfHvAK1IjXM6ZtmaaZcnUYT1K/imkZ91ayu5w6yLt1MwW+aqREVWb+49ZYDzfCFuOfUH7wNYnMkiRN1qwLojhXrVlRn/QRyAXmbisfHm40q0bFw9tv/TPvNLssiqi4iwO2Obub/lM25lZ9qOcyqWEHr9xATQdhQs6eYtzxNBohXbjjyKJ7K3AgMBAAECggEAAfVx2KsSXObvhR2Qcxo+aENsN+Cn/J7cHM3fNp1y/Pu9aBJpujLYB3w4Q+Fog9Y43Zz9kSx5rhmrCdG44x+GBGXoIf91HgcilLSC5lbAR/k+vUh7hOmUFcHGK0+JP5g2OcH73NMolfqxej+IrmUEcRvKRC3MlWMYvgW6YeusM/7EozZgF4pzoiy15OU/MFYD6QIaPCcWZmpFkBXz0JQijUzrDu+y6t1N0SzJokX9X4rbqLKPO3UPJZIhCJ4WkVlP/p54BT+AMgExyUfdD1q1H6ZrqNbREmH76K1ebviorNLouqzy5Vr73JedM6wNFeid0aD0XXWOCjHVK8H3DU5FCQKBgQDDITargdKJColTjl6wU7uIhEQ7dXctbWiyfswUi3wb3CeA7tKSQnsZTYDfFc6wMEnNxPhbTzb/Q0cUI7PUdxLEZIQSIVl2+13pqV6qKm8PYBstcIHtaNaB05pgfSknyITqG9DMntIOuBp1ltueTDraMn8lYOD5g9TV/+RAa5z2EwKBgQDOjHLObMioLAxH3f315yodCquOcYT3vAI12tKar6pdlxc0Z3FnmjKYiATSD3P1qbRzAHCDqXfrAgjbsx4plXc8xnEIxjxZBpJMABgCl/zK/xEHyZ8dgCr8FLCvhOW3wv/CpzDbm1KpahTanQhEhSKXERK22L50Zyh3js1Ubfl1TQKBgBNL6I0jZH+a5CO4M5L6ZNRGSD0dC7EZXb4xHdt2Q8q5hcqRU4+VNXk2GeV10Z/I1rObo/fbqJOrwo6yTSlYsSlsy0bDt4Y1q37c+fiYA62gkm927dJdiMED/QNHvVcq1EIWiBqEJj/AYxV32rYX0cYcMkivAPCL4fNbv+XC/p2zAoGAIp1I9C0o534SRM0ALYCi/yD1pTaDCR1Z5XqZhtDfpTWX7vFTAQDHb+aDoEx0q3vYQNmXAYmaDilWILOA34kr5WSANu8519WRGOl/HJgqBj7+tKZmYwRCr+Irxg5ojQZB5HYuau85yCh9/DEK3KjPJi/3SetC57EOCBNHd9nCT5UCgYEAghMoFFzoPgdNPwz5Y+jW8kYtRPDCj9BZTBrvFZp13vR79oDrfDTSvRa5VmDy0qIhHHM9Ydr2QpO01jFwjUk8AnTTariK/p0JcA1ElDX4Q1jdEqP1ncJsiI73qk+k30WW9Uu/ZCmUFDyYIWuVgMjesUUDspQy/dpqQgdJRgkWBQQ=',
            s)
        print(sign)
