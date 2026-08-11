[app]

# 应用标题（手机桌面上显示的名字）
title = 爱奇艺云包场

# 包名（只能小写英文、数字、下划线）
package.name = iqiyiclaim

# 域名（反写，随便填）
package.domain = com.example

# 源代码目录
source.dir = .

# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# 版本号
version = 0.1

# 依赖库（你代码里 import 了 requests 和 kivy，必须写这里）
requirements = python3,kivy,requests,urllib3,charset_normalizer,certifi,idna

# 屏幕方向 portrait=竖屏
orientation = portrait

# 是否全屏 0=否
fullscreen = 0

# Android API 版本
android.api = 33

# 最低支持的安卓版本
android.minapi = 21

# 打包的 CPU 架构（arm64 是现在主流手机）
android.archs = arm64-v8a, armeabi-v7a
android.build_tools = 33.0.0

# 网络权限（必须！你的代码要发 HTTP 请求）
android.permissions = INTERNET


[buildozer]

# 日志详细程度
log_level = 2

# 是否在根目录运行警告
warn_on_root = 1
