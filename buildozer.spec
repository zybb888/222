[app]
#标题允许中文 title language is not limited
title = 爱奇艺助手
package.name = iqiyihelper

#release模式不能用org.test 'org.test' can't be used in release mode
package.domain = org.example
#工作目录 working directory
source.dir = .
#需要打包的文件类型 file types to be packed
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
#依赖库
requirements = python3,kivy==2.3.0,requests,certifi,urllib3,chardet,idna

# --- Android 配置 ---
android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.allow_api_min = 21
# NDK 25c 与 p4a master 兼容，解决 NDK 版本冲突（之前 25b 不兼容）
android.ndk = 25c
android.ndkVersion = 25c
android.ndk_api = 21
android.archs = arm64-v8a
# 自动接受 SDK 许可证
android.accept_sdk_license = True
# 跳过 buildozer 自动下载 SDK/NDK/p4a（已在 workflow 中预下载）
android.skip_update = True

# --- Gradle 配置 ---
android.gradle_download = https:gradle-7.6.4-all.zip
android.gradle_plugin = 7.4.2

# --- p4a 配置 ---
p4a.bootstrap = sdl2
p4a.gradle_options = -Dorg.gradle.java.home=/usr/lib/jvm/temurin-17-jdk-amd64

# 排除测试文件
exclude_patterns = **/test/*, **/tests/*

[buildozer]
log_level = 2
warn_on_root = 0
