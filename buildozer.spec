[app]
title = 爱奇艺助手
package.name = iqiyihelper
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,requests,certifi,urllib3,chardet,idna

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndkVersion = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
