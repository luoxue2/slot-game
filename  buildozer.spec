[app]
title = Slot Machine
package.name = slotgame
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav
version = 1.0
requirements = python3,kivy==2.1.0,pygame,numpy
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.arch = arm64-v8a
android.api = 34
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
log_level = 2

[buildozer]
build_dir = .buildozer