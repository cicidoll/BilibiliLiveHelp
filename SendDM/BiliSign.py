from hashlib import md5
from os import path, getcwd
from urllib.parse import urlencode
from apscheduler.schedulers.blocking import BlockingScheduler
from plugin.Logger import logger
from Model import room_config
import asyncio, json, os, random, sys, time, httpx, qrcode_terminal, nest_asyncio

nest_asyncio.apply()
sys.path.append(".")

class VarifyTokenError(Exception):
    """验证token错误"""


class ApiTvLogin:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
                                     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88\
                                      Safari/537.36 Edg/87.0.664.60',
            'Referer': 'https://www.bilibili.com/'
        }
        self.local_id = 0
        self.auth_code = None
        self.app_key = "4409e2ce8ffd12b8"
        self.app_sec = "59b43e04ad6965f34319062b478f83dd"

    async def get_auth_code(self):
        """
        获取用于制作扫码登录的二维码的链接和用于查看是否扫码登录成功的auth_code
        :return:
        """

        params: dict = {'local_id': self.local_id, 'appkey': self.app_key, 'ts': int(time.time())}
        params['sign'] = md5(f"{urlencode(sorted(params.items()))}{self.app_sec}".encode('utf-8')).hexdigest()
        try:
            async with httpx.AsyncClient(headers=self.headers) as session:
                url = "https://passport.bilibili.com/x/passport-tv-login/qrcode/auth_code"
                response = await session.post(url, data=params)
                data = response.json()
                self.auth_code = data["data"]["auth_code"]
                logger.info("获取auth_code成功")
                # logger.info(data)
                return data["data"]["url"]
        except Exception as e:
            logger.error(e)

    # 获取token
    async def get_token(self):

        params: dict = {'local_id': self.local_id, 'appkey': self.app_key, 'ts': int(time.time()),
                        'auth_code': self.auth_code}
        params['sign'] = md5(f"{urlencode(sorted(params.items()))}{self.app_sec}".encode('utf-8')).hexdigest()
        try:
            url = "https://passport.bilibili.com/x/passport-tv-login/qrcode/poll"
            async with httpx.AsyncClient(headers=self.headers) as session:
                response = await session.post(url, data=params)
                return response.json()
        except Exception as e:
            logger.error(e)

    # 刷新cookie
    async def refresh_cookie(self, access_token: str, refresh_token: str):
        params: dict = {'access_token': access_token, 'refresh_token': refresh_token,
                        'appkey': self.app_key}
        params['sign'] = md5(f"{urlencode(sorted(params.items()))}{self.app_sec}".encode('utf-8')).hexdigest()
        try:
            url = "https://passport.bilibili.com/api/v2/oauth2/refresh_token"
            async with httpx.AsyncClient(headers=self.headers) as session:
                response = await session.post(url, data=params)
                return response.json()
        except Exception as e:
            logger.error(e)


class Login:
    def __init__(self):
        self.base_path = path.dirname(path.abspath(__file__))
        self.access_token = None

    async def make_qrcode(self, url):
        qrcode_terminal.draw(url)

    async def get_token(self, login: ApiTvLogin):
        start = time.time()
        while True:
            if time.time() - start > 150:
                logger.error("登录超时")
                break
            scan_result = await login.get_token()
            if scan_result["code"] == 0:
                with open("AuthInfo.json", "w+") as f:
                    data = {"token_info": scan_result["data"]["token_info"]}
                    f.write(json.dumps(data))
                    self.access_token = scan_result["data"]["token_info"]["access_token"]
                logger.info("登录成功")
                break
            if scan_result["code"] == -3:
                logger.error("API校验密匙错误")
                sys.exit()
            if scan_result["code"] == -400:
                logger.error("请求错误")
                sys.exit()
            if scan_result["code"] == 86038:
                logger.error("二维码已失效")
                sys.exit()
            if scan_result["code"] == 86039:
                logger.info("等待扫码中")
            await asyncio.sleep(3)

    async def login(self):
        logger.info("为保证能够显示二维码,请将窗口最大化")
        login_class = ApiTvLogin()
        auth_url = await login_class.get_auth_code()
        await asyncio.gather(*[self.make_qrcode(auth_url), self.get_token(login_class)])


class TasksApi:
    def __init__(self, access_token):
        self.access_token = access_token
        self.app_key = "1d8b6e7d45233436"
        self.app_sec = "560c52ccd288fed045859ed18bffd973"
        self.headers = {
            "User-Agent": "Mozilla/5.0 BiliDroid/6.73.1 (bbcallen@gmail.com) os/android model/Mi 10 Pro mobi_app/android build/6731100 channel/xiaomi innerVer/6731110 osVer/12 network/2",
        }
        self.medal_list = []

    async def sendDanmaku(self, message: str):
        '''
        发送弹幕
        '''
        url = "https://api.live.bilibili.com/xlive/app-room/v1/dM/sendmsg"
        room_id = room_config.roomid
        params: dict = {
            "access_key": self.access_token,
            "actionKey": "appkey",
            "appkey": self.app_key,
            "ts": int(time.time()),
        }
        data = {
            "cid": room_id,
            "msg": message,
            "rnd": int(time.time()),
            "color": "16777215",
            "fontsize": "25",
        }
        params['sign'] = md5(f"{urlencode(sorted(params.items()))}{self.app_sec}".encode('utf-8')).hexdigest()
        self.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        try:
            async with httpx.AsyncClient(headers=self.headers) as session:
                result = await session.post(url, params=params, data=data)
                result_js = result.json()
                logger.info(f"[{room_id}][成功]发送了弹幕:{json.loads(result_js['data']['mode_info']['extra'])['content']}")
        except:
            logger.exception("What?!")
            logger.error(f"{room_id}[失败]发送弹幕失败")

    async def loginVerify(self):
        '''
        登录验证
        '''
        url = "https://app.bilibili.com/x/v2/account/mine"
        params: dict = {
            "access_key": self.access_token,
            "actionKey": "appkey",
            "appkey": self.app_key,
            "ts": int(time.time()),
        }
        params['sign'] = md5(f"{urlencode(sorted(params.items()))}{self.app_sec}".encode('utf-8')).hexdigest()
        async with httpx.AsyncClient(headers=self.headers) as session:
            result = await session.get(url, params=params)
        return result.json()


class Main:
    def __init__(self):
        self.base_path = getcwd()
        self.access_token = None

    async def run(self, message):
        await self.get_access_token()
        if not self.access_token:
            logger.error("获取access_token失败,请重试")
            sys.exit()
        tasks_api = TasksApi(self.access_token)
        await asyncio.gather(
            tasks_api.sendDanmaku(message)
        )

    async def get_access_token(self):
        file_path = path.join(self.base_path, "AuthInfo.json")
        if path.exists(file_path):
            """如果保存的有access_token就读取"""
            try:
                with open(file_path, "r") as f:
                    token_info = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                """如果文件内的内容被删掉了"""
                await Login().login()
                with open(file_path, "r") as f:
                    file_content = f.read()
                    token_info = json.loads(file_content)
            try:
                access_token = token_info["token_info"]["access_token"]
                result = await TasksApi(access_token).loginVerify()
                if not result["data"]["name"]:
                    raise VarifyTokenError("验证token失败")
                logger.info(f"当前帐号：{result['data']['name']}")
                self.access_token = access_token
            except VarifyTokenError:
                """如果验证失败了就刷新access_token"""
                access_token = token_info["token_info"]["access_token"]
                refresh_token = token_info["token_info"]["refresh_token"]
                result = await ApiTvLogin().refresh_cookie(access_token, refresh_token)
                with open("AuthInfo.json", "w+") as f:
                    data = {"token_info": result["data"]["token_info"]}
                    f.write(json.dumps(data))
                self.access_token = result["data"]["token_info"]["access_token"]
        else:
            await Login().login()
            with open(file_path, "r") as f:
                file_content = f.read()
                token_info = json.loads(file_content)
            access_token = token_info["token_info"]["access_token"]
            result = await TasksApi(access_token).loginVerify()
            logger.info(f"当前帐号：{result['data']['name']}")
            self.access_token = access_token


class BiliSendDM:

    def send_message(self, message):
        """ 发送弹幕 """
        def run():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(Main().run(message))
        try:
            run()
        except KeyboardInterrupt:
            logger.info("退出")       