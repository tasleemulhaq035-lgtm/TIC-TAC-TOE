[app]
title = TIC TAC TOE
package.name = tictactoe
package.domain = org.gemu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
icon.filename = logo.png
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
