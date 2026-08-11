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
android.allow_api_min = 21
android.ndk = 25b
android.ndkVersion = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.sdk = 33

android.gradle_download = https:gradle-7.6.4-all.zip
android.gradle_plugin = 7.4.2

p4a.bootstrap = sdl2
p4a.gradle_options = -Dorg.gradle.java.home=/usr/lib/jvm/temurin-17-jdk-amd64

exclude_patterns = **/test/*, **/tests/*

[buildozer]
log_level = 2
warn_on_root = 0
