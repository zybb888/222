[app]
# 应用标题
title = 爱奇艺领取

# 包名和域名
package.name = iqiyiclaim
package.domain = org.iqiyi.claim

# 源代码目录
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# 严格排除无关文件，减少打包体积和编译负担
source.exclude_dirs = tests, bin, venv, .buildozer, .git, logs_85343046343, logs_85348553101

# 版本号
version = 0.1

# 强制 Python 版本
python_version = 3.11

# 依赖项：必须包含 openssl 才能支持 https 请求
requirements = python3,kivy==2.2.1,requests,urllib3,certifi,idna,charset-normalizer,openssl

# 屏幕方向
orientation = portrait

# 权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# 编译环境设置
android.api = 31
android.minapi = 21
android.sdk = 31
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
