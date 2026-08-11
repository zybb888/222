[app]
title = 爱奇艺助手
package.name = iqiyihelper
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,requests,certifi,urllib3,chardet,idna

# --- 核心修复配置 ---
# 1. 使用模板中验证过的稳定版本组合
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_api = 21

# 2. 指定 Gradle 版本，避免下载失败或版本不兼容
android.gradle_download = https://services.gradle.org/distributions/gradle-7.6.4-all.zip
android.gradle_plugin = 7.4.2

# 3. 明确指定构建架构，使用新版的 archs 配置
android.archs = arm64-v8a

# 4. 自动接受 SDK 许可证
android.accept_sdk_license = True

# 5. 移除 p4a.branch 配置，使用 buildozer 自带的稳定版 p4a，避免版本冲突
# p4a.branch = master  <-- 已移除

# 权限
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
