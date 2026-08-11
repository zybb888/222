[app]
title = 爱奇艺助手
package.name = iqiyihelper
package.domain = org.example

# 指向你的主文件
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy,requests,urllib3,chardet,idna

# Android 特定设置
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a

[buildozer]
log_level = 2
