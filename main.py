#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爱奇艺云包场单账号领取工具 (Kivy Android版)
============================================
- 单账号，仅输入Cookie
- 支持立即开始和定时开始
- 自动重试，间隔0.5~1秒
- 无验证码弹窗，遇到验证码直接重试
- 默认最长120秒
"""

import re
import json
import time
import random
import threading
from datetime import datetime
from urllib.parse import quote

import requests

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

# ============= 常量 =============
CLAIM_API_URL = "https://act.vip.iqiyi.com/cloud-party-v2/seat/receive"
ADD_WHITELIST_URL = "https://serv.vip.iqiyi.com/view-engine/op/whitelist/add"

CODE_SUCCESS = "A00000"
CODE_NEED_CAPTCHA = "E00013"
CODE_NOT_ENOUGH = "Q00101"
CODE_SOLD_OUT = "Q00303"
CODE_ALREADY_GOT = "Q00301"

# ============= 账号解析 =============
class Account:
    def __init__(self, cookie: str = ""):
        self.cookie = cookie
        self.geetest_token = ""

    def parse_cookie(self) -> dict:
        cookies = {}
        cleaned = self.cookie.replace("\n", "; ").replace(", ", "; ")
        for match in re.finditer(r"([^=;\s]+)=([^;]*)", cleaned):
            name = match.group(1).strip()
            value = match.group(2).strip()
            if name and name not in ("Cookie", "cookie"):
                cookies[name] = value
        return cookies

    def get_param(self, key: str) -> str:
        return self.parse_cookie().get(key, "")

    @property
    def device_id(self) -> str:
        return self.get_param("QC006")

    @property
    def dfp(self) -> str:
        raw = self.get_param("__dfp")
        return raw.split("@")[0] if "@" in raw else raw

    @property
    def fv(self) -> str:
        return self.get_param("QC142")

    @property
    def session_id(self) -> str:
        return self.get_param("vipfe_device_session_id")

    @property
    def p00001(self) -> str:
        return self.get_param("P00001")

    @property
    def fr_version(self) -> str:
        dev = self.device_id
        sid = self.session_id
        if dev and sid:
            return quote(f"v=&d={dev}&sid={sid}")
        return ""

    @property
    def cookie_header(self) -> str:
        c = self.parse_cookie()
        return "; ".join(f"{k}={v}" for k, v in c.items() if v)

    def is_valid(self) -> tuple[bool, str]:
        if not self.cookie.strip():
            return False, "Cookie为空"
        if not self.p00001:
            return False, "缺少P00001"
        if not self.device_id:
            return False, "缺少QC006"
        if not self.dfp:
            return False, "缺少__dfp"
        if not self.fv:
            return False, "缺少QC142"
        return True, ""

# ============= 领取引擎 =============
class ClaimEngine:
    def __init__(self, account: Account, activity_code: str, item_code: str, act_code: str, log_callback=None):
        self.account = account
        self.activity_code = activity_code
        self.item_code = item_code
        self.act_code = act_code
        self.log = log_callback or (lambda msg: None)
        self.running = False
        self.success = False
        self.sold_out = False
        self.total_requests = 0
        self.last_code = ""
        self.last_msg = ""

    def _base_params(self):
        a = self.account
        return {
            "page": "30", "abt": "", "u": a.device_id,
            "deviceIdType": "1003", "platform": "97ae2982356f69d8",
            "version": "1.0.0", "deviceId": a.device_id,
            "qyid": a.device_id, "dfp": a.dfp,
            "lang": "zh_CN", "app_lm": "cn",
            "ptid": "03020031010000000000", "agentType": "11",
            "fv": a.fv, "source": a.fv, "cs": "1",
            "activityCode": self.activity_code,
        }

    def _headers(self):
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "https://vip.iqiyi.com",
            "Referer": "https://vip.iqiyi.com/",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Cookie": self.account.cookie_header,
        }

    def do_signup(self) -> bool:
        act_code = self.act_code or self.activity_code
        params = {**self._base_params(), "actCode": act_code, "_": str(int(time.time() * 1000))}
        try:
            resp = requests.get(ADD_WHITELIST_URL, headers=self._headers(), params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("code") == CODE_SUCCESS
        except Exception:
            pass
        return False

    def send_claim(self) -> dict:
        a = self.account
        data = {
            **self._base_params(),
            "de": a.geetest_token or "",
            "fr_version": a.fr_version,
            "itemCode": self.item_code,
            "_": str(int(time.time() * 1000)),
            "token": "",
        }
        try:
            resp = requests.post(CLAIM_API_URL, headers=self._headers(), data=data, timeout=5)
            self.total_requests += 1
            result = resp.json()
            code = str(result.get("code", ""))
            msg = str(result.get("msg", ""))
            self.last_code = code
            self.last_msg = msg
            return {"code": code, "msg": msg, "raw": result}
        except requests.exceptions.Timeout:
            self.total_requests += 1
            return {"code": "TIMEOUT", "msg": "请求超时", "raw": {}}
        except Exception as e:
            self.total_requests += 1
            return {"code": "EXCEPTION", "msg": str(e)[:80], "raw": {}}

    def run_sync(self, max_duration: float = 120):
        self.running = True
        self.success = False
        self.sold_out = False
        self.total_requests = 0
        self.log("开始领取！默认最长120秒")

        signup_ok = self.do_signup()
        self.log(f"报名刷新{'成功' if signup_ok else '失败'}")

        start_time = time.time()

        while self.running:
            elapsed = time.time() - start_time
            if elapsed > max_duration:
                self.log(f"超时({max_duration}s)，停止领取")
                break
            if self.success or self.sold_out:
                break

            resp = self.send_claim()
            code = resp.get("code", "?")
            msg = resp.get("msg", "")

            if code == CODE_NEED_CAPTCHA:
                self.log(f"触发验证码，跳过继续重试...")
            elif code == CODE_SUCCESS:
                self.log(f"领取成功！")
                self.success = True
                break
            elif code == CODE_SOLD_OUT:
                self.log(f"已领光")
                self.sold_out = True
                break
            elif code == CODE_ALREADY_GOT:
                self.log(f"已领取过")
                self.success = True
                break
            elif code == CODE_NOT_ENOUGH:
                pass
            elif code in ("TIMEOUT", "EXCEPTION"):
                self.log(f"请求异常: {msg}")
            else:
                self.log(f"响应: {code} | {msg[:60]}")

            sleep_time = random.uniform(0.5, 1.0)
            time.sleep(sleep_time)

        status = "领取成功" if self.success else ("已领光" if self.sold_out else "已停止/超时")
        self.log(f"领取结束: {status} (总请求{self.total_requests}次)")
        self.running = False

    def stop(self):
        self.running = False

# ============= Kivy GUI =============
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 5
        self.engine = None
        self._thread = None

        # --- Cookie输入 ---
        self.add_widget(Label(text='Cookie:', size_hint_y=None, height=30, halign='left', color=(0,0,0,1)))
        self.cookie_input = TextInput(
            multiline=True, height=120, size_hint_y=None,
            hint_text='粘贴完整Cookie...',
            foreground_color=(0,0,0,1), background_color=(1,1,1,1)
        )
        self.add_widget(self.cookie_input)

        # --- 参数输入 ---
        grid = GridLayout(cols=2, spacing=5, size_hint_y=None, height=200)

        grid.add_widget(Label(text='场次代码(itemCode):', size_hint_y=None, height=30, color=(0,0,0,1)))
        self.item_input = TextInput(multiline=False, size_hint_y=None, height=40, hint_text='如: xxxxxx', foreground_color=(0,0,0,1))
        grid.add_widget(self.item_input)

        grid.add_widget(Label(text='活动代码(activityCode):', size_hint_y=None, height=30, color=(0,0,0,1)))
        self.act_input = TextInput(multiline=False, size_hint_y=None, height=40, hint_text='如: a687d61142dbd753', foreground_color=(0,0,0,1))
        grid.add_widget(self.act_input)

        grid.add_widget(Label(text='白名单actCode:', size_hint_y=None, height=30, color=(0,0,0,1)))
        self.whitelist_input = TextInput(multiline=False, size_hint_y=None, height=40, hint_text='留空则使用活动代码', foreground_color=(0,0,0,1))
        grid.add_widget(self.whitelist_input)

        grid.add_widget(Label(text='目标时间(HH:MM:SS):', size_hint_y=None, height=30, color=(0,0,0,1)))
        self.time_input = TextInput(multiline=False, size_hint_y=None, height=40, hint_text='如: 18:00:00', foreground_color=(0,0,0,1))
        grid.add_widget(self.time_input)

        self.add_widget(grid)

        # --- 按钮 ---
        btn_box = BoxLayout(size_hint_y=None, height=55, spacing=10)
        self.btn_now = Button(text='立即开始', on_press=self.start_now, background_color=(0.2, 0.6, 0.2, 1))
        self.btn_timer = Button(text='定时开始', on_press=self.start_timer, background_color=(0.2, 0.4, 0.8, 1))
        self.btn_stop = Button(text='停止', on_press=self.stop_claim, disabled=True, background_color=(0.8, 0.2, 0.2, 1))
        btn_box.add_widget(self.btn_now)
        btn_box.add_widget(self.btn_timer)
        btn_box.add_widget(self.btn_stop)
        self.add_widget(btn_box)

        # --- 日志 ---
        self.add_widget(Label(text='运行日志:', size_hint_y=None, height=30, halign='left', color=(0,0,0,1)))
        scroll = ScrollView()
        self.log_label = Label(
            text='', markup=True, size_hint_y=None,
            valign='top', halign='left', color=(0.1,0.1,0.1,1)
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)

    def log(self, msg: str):
        now = datetime.now().strftime("%H:%M:%S")
        line = f"[{now}] {msg}"
        def update(dt):
            current = self.log_label.text
            lines = current.split('\n')
            if len(lines) > 200:
                lines = lines[-200:]
                current = '\n'.join(lines)
            self.log_label.text = current + line + '\n'
        Clock.schedule_once(update)

    def _get_inputs(self):
        return {
            'cookie': self.cookie_input.text.strip(),
            'item': self.item_input.text.strip(),
            'activity': self.act_input.text.strip(),
            'whitelist': self.whitelist_input.text.strip(),
            'target_time': self.time_input.text.strip(),
        }

    def _validate(self, inputs):
        if not inputs['cookie']:
            self.log("[错误] Cookie不能为空")
            return None
        if not inputs['item']:
            self.log("[错误] 场次代码不能为空")
            return None
        if not inputs['activity']:
            self.log("[错误] 活动代码不能为空")
            return None

        account = Account(cookie=inputs['cookie'])
        ok, err = account.is_valid()
        if not ok:
            self.log(f"[错误] {err}")
            return None
        return account

    def _set_buttons(self, running: bool):
        def update(dt):
            self.btn_now.disabled = running
            self.btn_timer.disabled = running
            self.btn_stop.disabled = not running
        Clock.schedule_once(update)

    def start_now(self, instance):
        inputs = self._get_inputs()
        account = self._validate(inputs)
        if not account:
            return

        self.log("=" * 30)
        self.log("立即开始领取...")

        self.engine = ClaimEngine(
            account=account,
            activity_code=inputs['activity'],
            item_code=inputs['item'],
            act_code=inputs['whitelist'] or inputs['activity'],
            log_callback=self.log
        )
        self._set_buttons(True)

        def run():
            self.engine.run_sync(max_duration=120)
            Clock.schedule_once(lambda dt: self._set_buttons(False), 0)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def start_timer(self, instance):
        inputs = self._get_inputs()
        account = self._validate(inputs)
        if not account:
            return

        target_time_str = inputs['target_time']
        if not target_time_str:
            self.log("[错误] 请输入目标时间")
            return

        try:
            h, m, s = map(int, target_time_str.split(":"))
        except ValueError:
            self.log("[错误] 时间格式应为 HH:MM:SS")
            return

        now = datetime.now()
        target = now.replace(hour=h, minute=m, second=s, microsecond=0)
        if target <= now:
            target = target.replace(day=target.day + 1)

        wait_seconds = (target - now).total_seconds()
        self.log(f"定时目标: {target_time_str}，等待 {wait_seconds:.0f} 秒后开始")

        self._set_buttons(True)

        def run():
            time.sleep(wait_seconds)
            if self.engine and not getattr(self.engine, 'running', True):
                return
            self.log("定时时间到，开始领取！")
            self.engine = ClaimEngine(
                account=account,
                activity_code=inputs['activity'],
                item_code=inputs['item'],
                act_code=inputs['whitelist'] or inputs['activity'],
                log_callback=self.log
            )
            self.engine.run_sync(max_duration=120)
            Clock.schedule_once(lambda dt: self._set_buttons(False), 0)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop_claim(self, instance):
        if self.engine:
            self.engine.stop()
            self.log("已发送停止信号")
        self._set_buttons(False)

class IqiyiApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        return MainLayout()

if __name__ == '__main__':
    IqiyiApp().run()
