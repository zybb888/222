import threading
import time
import re
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import mainthread

CLAIM_API_URL = "https://act.vip.iqiyi.com/cloud-party-v2/seat/receive"
ADD_WHITELIST_URL = "https://serv.vip.iqiyi.com/view-engine/op/whitelist/add"
CODE_SUCCESS = "A00000"
CODE_NEED_CAPTCHA = "E00013"
CODE_SOLD_OUT = "Q00303"
CODE_ALREADY_GOT = "Q00301"


class IqiyiClaimApp(App):
    def build(self):
        self.title = "爱奇艺云包场助手"
        self.running = False
        self.thread = None

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input_scroll = ScrollView(size_hint_y=None, height=320)
        self.input_box = BoxLayout(orientation='vertical', size_hint_y=None, height=320, spacing=5)
        self.input_scroll.add_widget(self.input_box)

        self.cookie_input = TextInput(hint_text="Cookie (P00001...)", multiline=True, size_hint_y=None, height=120)
        self.item_code_input = TextInput(hint_text="场次代码 (itemCode)", multiline=False, size_hint_y=None, height=40)
        self.activity_code_input = TextInput(hint_text="活动代码 (activityCode)", text="a687d61142dbd753", multiline=False, size_hint_y=None, height=40)
        self.act_code_input = TextInput(hint_text="白名单代码 (actCode)", multiline=False, size_hint_y=None, height=40)
        self.max_time_input = TextInput(hint_text="最大运行时间(秒)", text="120", multiline=False, size_hint_y=None, height=40)

        self.input_box.add_widget(self.cookie_input)
        self.input_box.add_widget(self.item_code_input)
        self.input_box.add_widget(self.activity_code_input)
        self.input_box.add_widget(self.act_code_input)
        self.input_box.add_widget(self.max_time_input)

        self.layout.add_widget(Label(text="参数设置:", size_hint_y=None, height=30))
        self.layout.add_widget(self.input_scroll)

        self.btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.start_btn = Button(text="立即开始", on_press=self.start_task)
        self.stop_btn = Button(text="停止", on_press=self.stop_task, disabled=True)
        self.btn_layout.add_widget(self.start_btn)
        self.btn_layout.add_widget(self.stop_btn)
        self.layout.add_widget(self.btn_layout)

        self.layout.add_widget(Label(text="日志输出:", size_hint_y=None, height=30))

        self.log_scroll = ScrollView()
        self.log_output = Label(text="", size_hint_y=None, valign='top', halign='left', markup=True)
        self.log_output.bind(texture_size=self.log_output.setter('size'))
        self.log_scroll.add_widget(self.log_output)
        self.layout.add_widget(self.log_scroll)

        return self.layout

    def log(self, msg):
        print(msg)
        self.update_log(msg)

    @mainthread
    def update_log(self, msg):
        current = self.log_output.text
        self.log_output.text = f"{current}\n{msg}"
        self.log_scroll.scroll_to(self.log_output)

    def start_task(self, instance):
        if not self.cookie_input.text.strip():
            self.log("[错误] 请输入 Cookie")
            return
        if not self.item_code_input.text.strip():
            self.log("[错误] 请输入场次代码")
            return

        self.running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.log("[状态] 任务已启动...")

        self.thread = threading.Thread(target=self.run_logic, daemon=True)
        self.thread.start()

    def stop_task(self, instance):
        self.running = False
        self.log("[状态] 正在停止...")
        self.start_btn.disabled = False
        self.stop_btn.disabled = True

    def run_logic(self):
        cookie = self.cookie_input.text.strip()
        item_code = self.item_code_input.text.strip()
        activity_code = self.activity_code_input.text.strip()
        act_code = self.act_code_input.text.strip()

        try:
            max_duration = int(self.max_time_input.text.strip())
        except Exception:
            max_duration = 120

        def get_cookie_val(key):
            match = re.search(rf"{key}=([^;]+)", cookie)
            return match.group(1) if match else ""

        p00001 = get_cookie_val("P00001")
        device_id = get_cookie_val("QC006")
        dfp = get_cookie_val("__dfp").split("@")[0]
        fv = get_cookie_val("QC142")

        if not all([p00001, device_id, dfp, fv]):
            self.log("[错误] Cookie 解析失败，缺少关键参数 (QC006, __dfp, QC142)")
            self.running = False
            self.start_btn.disabled = False
            self.stop_btn.disabled = True
            return

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Cookie": cookie,
            "Referer": "https://vip.iqiyi.com/"
        }

        signup_params = {
            "actCode": act_code or activity_code,
            "page": "30", "abt": "", "u": device_id, "deviceIdType": "1003",
            "platform": "97ae29823569d8", "version": "1.0.0", "deviceId": device_id,
            "qyid": device_id, "dfp": dfp, "lang": "zh_CN", "app_lm": "cn",
            "ptid": "03020031010000000000", "agentType": "11", "fv": fv, "source": fv, "cs": "1",
            "activityCode": activity_code, "_": str(int(time.time() * 1000))
        }

        try:
            r = requests.get(ADD_WHITELIST_URL, headers=headers, params=signup_params, timeout=5)
            if r.status_code == 200 and r.json().get("code") == CODE_SUCCESS:
                self.log("[系统] 报名成功")
            else:
                self.log(f"[系统] 报名可能失败或已报名: {r.text[:80]}")
        except Exception as e:
            self.log(f"[系统] 报名请求异常: {e}")

        start_time = time.time()

        while self.running:
            if time.time() - start_time > max_duration:
                self.log(f"[系统] 达到最大运行时间 ({max_duration}s)，自动停止")
                self.running = False
                break

            data = {
                "page": "30", "abt": "", "u": device_id, "deviceIdType": "1003",
                "platform": "97ae29823569d8", "version": "1.0.0", "deviceId": device_id,
                "qyid": device_id, "dfp": dfp, "lang": "zh_CN", "app_lm": "cn",
                "ptid": "03020031010000000000", "agentType": "11", "fv": fv, "source": fv, "cs": "1",
                "activityCode": activity_code, "de": "",
                "fr_version": f"v=&d={device_id}&sid={get_cookie_val('vipfe_device_session_id')}",
                "itemCode": item_code, "_": str(int(time.time() * 1000)), "token": ""
            }

            try:
                r = requests.post(CLAIM_API_URL, headers=headers, data=data, timeout=5)
                res = r.json()
                code = res.get("code", "")
                msg = res.get("msg", "")

                if code == CODE_SUCCESS:
                    self.log(f"[成功] 领取成功！Msg: {msg}")
                    self.running = False
                elif code == CODE_SOLD_OUT:
                    self.log(f"[结束] 已领光")
                    self.running = False
                elif code == CODE_ALREADY_GOT:
                    self.log(f"[提示] 已领取过")
                    self.running = False
                elif code == CODE_NEED_CAPTCHA:
                    self.log("[风控] 触发验证码 (E00013)，自动重试中...")
                else:
                    self.log(f"[响应] {code}: {msg}")

            except Exception as e:
                self.log(f"[错误] 请求异常: {e}")

            time.sleep(0.5 + (0.5 * (hash(str(time.time())) % 100) / 100))

        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.log("[状态] 任务已结束")


if __name__ == '__main__':
    IqiyiClaimApp().run()
