[app]
title = 爱奇艺助手
package.name = iqiyihelper
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy==2.3.0,requests,certifi,urllib3,chardet,idna

# Android 配置
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 26b
android.ndkVersion = 26b.1.9797547
android.archs = arm64-v8a

# 自动接受 SDK 许可证
android.accept_sdk_license = True

# 使用 p4a master 分支（最新修复）
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
