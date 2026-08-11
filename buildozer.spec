[app]
# 应用标题
title = 爱奇艺领取

# 包名和域名
package.name = iqiyiclaim
package.domain = org.iqiyi.claim

# 源代码目录
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# 排除不必要的目录，减少编译负担
source.exclude_dirs = tests, bin, venv, .buildozer, .git

# 版本号
version = 0.1

# 强制 Python 版本，避免使用不稳定的 3.14
python_version = 3.11

# 依赖项：只需列出核心，Buildozer 会处理 requests 的子依赖
requirements = python3,kivy==2.2.1,requests,urllib3,certifi,idna,charset-normalizer

# 屏幕方向
orientation = portrait

# 权限：增加网络状态检查权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Android API 级别 (33 为当前主流标准)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a

# 自动同意 SDK 协议
android.accept_sdk_license = True

# 日志级别
log_level = 2

# 是否全屏
fullscreen = 0

[buildozer]
# 编译目录
build_dir = ./.buildozer
bin_dir = ./bin
