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
android.ndkVersion = 25b.8775140
android.arch = arm64-v8a
android.sdk = 28
android.compileSdk = 33

[buildozer]
log_level = 2
warn_on_root = 0
