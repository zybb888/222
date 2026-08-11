[app]
# 应用标题
title = 爱奇艺领取

# 包名和域名
package.name = iqiyiclaim
package.domain = org.iqiyi.claim

# 源代码目录
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# 排除日志和无关文件夹，加快打包速度
source.exclude_dirs = tests, bin, venv, .buildozer, .git, logs_85343046343, logs_85348553101

# 版本号
version = 0.1

# 强制使用稳定的 Python 3.11 核心
python_version = 3.11

# 依赖项：升级 Kivy 到 2.3.0
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,charset-normalizer,openssl

# 屏幕方向
orientation = portrait

# 权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# 编译环境设置
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
