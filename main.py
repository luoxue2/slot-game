#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水果老虎机 - Android 17+ 适配版
针对手机触屏优化，支持 Android 14/15 (API 34-35)
"""

import os
import sys
import random
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.config import Config

# Android 适配配置
if platform == 'android':
    # 请求权限（Android 13+ 需要）
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.INTERNET])

    # 设置窗口为全屏
    from kivy.core.window import Window

    Window.fullscreen = True


# 获取资源路径（支持打包后）
def resource_path(relative_path):
    """获取资源的绝对路径"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SoundManager:
    """音效管理器 - Android 适配版"""

    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.sounds = {}
        self.initialized = False

        # 获取音效目录
        if platform == 'android':
            # Android 上的路径
            from android.storage import app_storage_path
            sound_dir = os.path.join(app_storage_path(), "sounds")
        else:
            # 桌面环境
            if getattr(sys, 'frozen', False):
                sound_dir = os.path.join(os.path.dirname(sys.executable), "sounds")
            else:
                sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

        # 如果路径不存在，尝试其他位置
        if not os.path.exists(sound_dir):
            sound_dir = os.path.join(os.getcwd(), "sounds")

        if not os.path.exists(sound_dir):
            # 尝试 resource_path
            try:
                sound_dir = resource_path("sounds")
            except:
                pass

        self.sound_dir = sound_dir
        self._init_audio()
        self._load_sounds()

    def _init_audio(self):
        """初始化音频系统"""
        try:
            from kivy.core.audio import SoundLoader
            self.initialized = True
        except Exception as e:
            print(f"音频系统初始化失败: {e}")
            self.sound_enabled = False

    def _load_sounds(self):
        """加载音效文件"""
        if not self.initialized or not os.path.exists(self.sound_dir):
            self.sound_enabled = False
            return

        sound_files = {
            "spin": "spin.wav",
            "win": "win.wav",
            "jackpot": "jackpot.wav",
            "lose": "lose.wav",
            "bet": "bet.wav",
            "button": "button.wav",
            "error": "error.wav",
            "bgm": "bgm.wav"
        }

        for name, filename in sound_files.items():
            filepath = os.path.join(self.sound_dir, filename)
            if os.path.exists(filepath):
                try:
                    sound = SoundLoader.load(filepath)
                    if sound:
                        if name == "bgm":
                            sound.volume = 0.3
                            sound.loop = True
                        else:
                            sound.volume = 0.7
                        self.sounds[name] = sound
                except Exception as e:
                    print(f"加载音效失败 {filename}: {e}")
                    self.sounds[name] = None
            else:
                self.sounds[name] = None

    def play(self, sound_name):
        """播放音效"""
        if not self.sound_enabled or sound_name not in self.sounds:
            return

        sound = self.sounds[sound_name]
        if sound:
            try:
                if sound.state == 'play':
                    sound.stop()
                sound.play()
            except:
                pass

    def play_bgm(self):
        """播放背景音乐"""
        if not self.music_enabled or "bgm" not in self.sounds:
            return

        sound = self.sounds["bgm"]
        if sound and sound.state != 'play':
            try:
                sound.play()
            except:
                pass

    def stop_bgm(self):
        """停止背景音乐"""
        if "bgm" in self.sounds and self.sounds["bgm"]:
            try:
                self.sounds["bgm"].stop()
            except:
                pass

    def toggle_sound(self):
        """切换音效"""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.stop_bgm()
        else:
            self.play_bgm()
        return self.sound_enabled

    def toggle_music(self):
        """切换音乐"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_bgm()
        else:
            self.stop_bgm()
        return self.music_enabled


class ReelLabel(Label):
    """转轮标签 - 移动端优化"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = sp(40)  # 手机上字体稍小
        self.bold = True
        self.color = (0.2, 0.2, 0.2, 1)


class SlotMachineGame(BoxLayout):
    """老虎机游戏主界面 - Android 适配版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(8)
        self.spacing = dp(8)

        # 游戏变量
        self.balance = 0
        self.bet = 0
        self.spinning = False
        self.bet_placed = False
        self.celebration_event = None

        # 游戏配置
        self.SYMBOLS = ["🍌", "🍎", "🍉", "🍈", "🍑"]
        self.PASSWORD = "010101"
        self.EXCHANGE_RATE = 100

        # 音效管理器
        self.sound_manager = SoundManager()

        # 设置背景色
        Window.clearcolor = get_color_from_hex('#1a1a2e')

        # 创建界面
        self._create_ui()

        # 播放背景音乐
        Clock.schedule_once(lambda dt: self.sound_manager.play_bgm(), 1)

        # 显示兑换对话框
        Clock.schedule_once(lambda dt: self.show_exchange_dialog(), 0.8)

    def _create_ui(self):
        """创建用户界面 - 移动端优化"""

        # === 标题 ===
        title = Label(
            text="🎰 水果老虎机",
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex('#f1c40f'),
            size_hint_y=None,
            height=dp(50)
        )
        self.add_widget(title)

        # === 余额显示 ===
        self.balance_label = Label(
            text=f"💰 筹码: {self.balance}",
            font_size=sp(14),
            bold=True,
            color=(0.93, 0.95, 0.95, 1),
            size_hint_y=None,
            height=dp(35)
        )
        self.add_widget(self.balance_label)

        # === 转轮显示 ===
        reel_layout = GridLayout(
            cols=4,
            spacing=dp(4),
            padding=dp(8),
            size_hint_y=None,
            height=dp(100)
        )

        self.reels = []
        for i in range(4):
            reel = ReelLabel(text="❓")
            reel_layout.add_widget(reel)
            self.reels.append(reel)

        self.add_widget(reel_layout)

        # === 消息显示 ===
        self.message_label = Label(
            text="欢迎来到水果老虎机！",
            font_size=sp(13),
            bold=True,
            color=get_color_from_hex('#FFD700'),
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='middle',
            text_size=(Window.width - dp(20), None)
        )
        self.add_widget(self.message_label)

        # === 下注区域 ===
        bet_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),
            spacing=dp(5)
        )

        bet_layout.add_widget(Label(
            text="下注:",
            font_size=sp(13),
            bold=True,
            color=(0.93, 0.95, 0.95, 1),
            size_hint_x=0.25
        ))

        self.bet_input = TextInput(
            text="",
            font_size=sp(15),
            multiline=False,
            input_filter='int',
            size_hint_x=0.75,
            halign='center',
            background_color=(0.2, 0.2, 0.3, 1),
            foreground_color=(1, 1, 1, 1)
        )
        bet_layout.add_widget(self.bet_input)
        self.add_widget(bet_layout)

        # === 快速下注按钮 ===
        quick_bet_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(38),
            spacing=dp(3)
        )

        quick_amounts = [10, 50, 100, 500]
        for amount in quick_amounts:
            btn = Button(
                text=str(amount),
                font_size=sp(11),
                background_color=get_color_from_hex('#34495e'),
                on_press=lambda x, a=amount: self.quick_bet(a)
            )
            quick_bet_layout.add_widget(btn)

        # 全押按钮
        all_in_btn = Button(
            text="ALL IN",
            font_size=sp(11),
            background_color=get_color_from_hex('#e74c3c'),
            on_press=lambda x: self.all_in()
        )
        quick_bet_layout.add_widget(all_in_btn)
        self.add_widget(quick_bet_layout)

        # === 主要操作按钮 ===
        main_btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(55),
            spacing=dp(8)
        )

        self.bet_btn = Button(
            text="💰 确认下注",
            font_size=sp(15),
            bold=True,
            background_color=get_color_from_hex('#2980b9'),
            on_press=lambda x: self.place_bet()
        )
        main_btn_layout.add_widget(self.bet_btn)

        self.spin_btn = Button(
            text="🎰 开始旋转",
            font_size=sp(15),
            bold=True,
            background_color=get_color_from_hex('#27ae60'),
            disabled=True,
            on_press=lambda x: self.spin_reels()
        )
        main_btn_layout.add_widget(self.spin_btn)
        self.add_widget(main_btn_layout)

        # === 底部按钮 ===
        bottom_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(38),
            spacing=dp(4)
        )

        admin_btn = Button(
            text="🔑",
            font_size=sp(14),
            background_color=get_color_from_hex('#8e44ad'),
            on_press=lambda x: self.admin_mode()
        )
        bottom_layout.add_widget(admin_btn)

        sound_btn = Button(
            text="🔊",
            font_size=sp(14),
            background_color=get_color_from_hex('#3498db'),
            on_press=lambda x: self.toggle_sound()
        )
        bottom_layout.add_widget(sound_btn)

        reset_btn = Button(
            text="🔄",
            font_size=sp(14),
            background_color=get_color_from_hex('#f39c12'),
            on_press=lambda x: self.reset_game()
        )
        bottom_layout.add_widget(reset_btn)

        quit_btn = Button(
            text="✖",
            font_size=sp(14),
            background_color=get_color_from_hex('#c0392b'),
            on_press=lambda x: self.quit_game()
        )
        bottom_layout.add_widget(quit_btn)
        self.add_widget(bottom_layout)

        # === 规则说明 ===
        rules = Label(
            text="🎯 2个相同=2倍 | 3个=3倍 | 4个=4倍",
            font_size=sp(9),
            color=get_color_from_hex('#7f8c8d'),
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(rules)

    def show_exchange_dialog(self):
        """显示兑换对话框"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        content.add_widget(Label(
            text="请输入初始兑换金额（元）",
            font_size=sp(14),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(35)
        ))

        content.add_widget(Label(
            text="💰 1元 = 100筹码",
            font_size=sp(11),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(25)
        ))

        amount_input = TextInput(
            text="",
            font_size=sp(16),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(45),
            halign='center'
        )
        content.add_widget(amount_input)

        popup = Popup(
            title="🎰 初始兑换",
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=False,
            title_size=sp(16)
        )

        def confirm(instance):
            try:
                amount = int(amount_input.text) if amount_input.text else 0
                if amount > 0:
                    self.balance = amount * self.EXCHANGE_RATE
                    self.update_balance_display()
                    self.show_message(f"✅ 成功兑换 {self.balance} 筹码！")
                    self.sound_manager.play("bet")
                    popup.dismiss()
                else:
                    self.show_message("金额必须大于0！")
            except ValueError:
                self.show_message("请输入有效的数字！")

        confirm_btn = Button(
            text="✅ 确认兑换",
            size_hint_y=None,
            height=dp(45),
            background_color=get_color_from_hex('#27ae60'),
            on_press=confirm
        )
        content.add_widget(confirm_btn)

        popup.open()

    def quick_bet(self, amount):
        """快速下注"""
        if self.spinning:
            self.show_message("请等待当前旋转完成")
            return

        if self.bet_placed:
            self.show_message("已经下注，请先旋转！")
            return

        if amount > self.balance:
            self.show_message("筹码不足！")
            return

        self.bet_input.text = str(amount)
        self.place_bet()

    def all_in(self):
        """全押"""
        if self.spinning:
            self.show_message("请等待当前旋转完成")
            return

        if self.bet_placed:
            self.show_message("已经下注，请先旋转！")
            return

        if self.balance > 0:
            self.quick_bet(self.balance)
        else:
            self.show_message("没有筹码可以下注！")

    def place_bet(self, *args):
        """下注"""
        if self.spinning:
            self.show_message("正在旋转中，请稍候...")
            return

        if self.bet_placed:
            self.show_message("已经下注，请点击开始旋转！")
            return

        try:
            bet = int(self.bet_input.text) if self.bet_input.text else 0
        except ValueError:
            self.show_message("请输入有效的下注金额！")
            return

        if bet <= 0:
            self.show_message("下注金额必须大于0！")
        elif bet > self.balance:
            self.show_message("筹码不足！")
        else:
            self.bet = bet
            self.balance -= bet
            self.bet_placed = True

            # 重置转轮
            self.reset_reels()

            self.update_balance_display()
            self.spin_btn.disabled = False
            self.spin_btn.background_color = get_color_from_hex('#27ae60')
            self.bet_btn.disabled = True
            self.bet_btn.background_color = get_color_from_hex('#555555')
            self.bet_input.disabled = True

            self.show_message(f"✅ 已下注 {bet} 筹码！点击开始旋转！")
            self.sound_manager.play("bet")

    def reset_reels(self):
        """重置转轮"""
        for reel in self.reels:
            reel.text = "❓"

    def spin_reels(self, *args):
        """旋转老虎机"""
        if self.spinning or not self.bet_placed:
            return

        self.spinning = True
        self.spin_btn.disabled = True
        self.spin_btn.background_color = get_color_from_hex('#555555')

        self.sound_manager.play("spin")

        # 生成结果
        self.result = [random.choice(self.SYMBOLS) for _ in range(4)]

        # 开始旋转动画
        self.spin_count = 0
        self.max_spins = 15
        Clock.schedule_interval(self._spin_animation, 0.08)

    def _spin_animation(self, dt):
        """旋转动画"""
        self.spin_count += 1

        # 随机显示符号（所有窗格一起变化）
        for reel in self.reels:
            reel.text = random.choice(self.SYMBOLS)

        if self.spin_count >= self.max_spins:
            Clock.unschedule(self._spin_animation)
            # 显示结果
            for i, reel in enumerate(self.reels):
                reel.text = self.result[i]
            Clock.schedule_once(lambda dt: self.check_win(), 0.3)

    def check_win(self, *args):
        """检查中奖"""
        max_count = max(self.result.count(s) for s in self.SYMBOLS)

        if max_count >= 4:
            multiplier = 4
            prize = self.bet * multiplier
            self.balance += prize
            self.show_message(f"🎉 大奖！4个相同！{multiplier}倍！获得{prize}筹码！")
            self.sound_manager.play("jackpot")
        elif max_count == 3:
            multiplier = 3
            prize = self.bet * multiplier
            self.balance += prize
            self.show_message(f"🎉 3个相同！{multiplier}倍！获得{prize}筹码！")
            self.sound_manager.play("win")
        elif max_count == 2:
            multiplier = 2
            prize = self.bet * multiplier
            self.balance += prize
            self.show_message(f"👏 2个相同！{multiplier}倍！获得{prize}筹码！")
            self.sound_manager.play("win")
        else:
            self.show_message("😢 没有中奖，继续加油！")
            self.sound_manager.play("lose")

        # 重置游戏状态
        self.bet = 0
        self.bet_placed = False
        self.spinning = False
        self.update_balance_display()
        self.spin_btn.disabled = True
        self.spin_btn.background_color = get_color_from_hex('#555555')
        self.bet_btn.disabled = False
        self.bet_btn.background_color = get_color_from_hex('#2980b9')
        self.bet_input.disabled = False
        self.bet_input.text = ""

        # 检查余额
        if self.balance <= 0:
            Clock.schedule_once(lambda dt: self._check_balance(), 1.5)

    def _check_balance(self, *args):
        """检查余额"""
        if self.balance <= 0:
            self.show_message("筹码已用完！点击🔑兑换")

    def admin_mode(self, *args):
        """管理员模式"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        content.add_widget(Label(
            text="请输入管理员密码:",
            font_size=sp(14),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(35)
        ))

        password_input = TextInput(
            text="",
            font_size=sp(16),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            halign='center'
        )
        content.add_widget(password_input)

        self.error_label = Label(
            text="",
            font_size=sp(11),
            color=get_color_from_hex('#e74c3c'),
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(self.error_label)

        self.admin_attempts = 0

        popup = Popup(
            title="🔑 管理员验证",
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=False,
            title_size=sp(16)
        )

        def verify(instance):
            self.admin_attempts += 1
            if password_input.text == self.PASSWORD:
                self.sound_manager.play("win")
                popup.dismiss()
                Clock.schedule_once(lambda dt: self.show_exchange_amount_dialog(), 0.3)
            else:
                remaining = 3 - self.admin_attempts
                if remaining > 0:
                    self.error_label.text = f"密码错误！剩余{remaining}次"
                    password_input.text = ""
                else:
                    self.sound_manager.play("lose")
                    popup.dismiss()
                    self.show_message("验证失败！")

        confirm_btn = Button(
            text="✅ 验证",
            size_hint_y=None,
            height=dp(45),
            background_color=get_color_from_hex('#27ae60'),
            on_press=verify
        )
        content.add_widget(confirm_btn)

        popup.open()

    def show_exchange_amount_dialog(self):
        """显示兑换金额对话框"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        content.add_widget(Label(
            text="请输入兑换金额（元）:\n💰 1元 = 100筹码",
            font_size=sp(13),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        ))

        amount_input = TextInput(
            text="",
            font_size=sp(16),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(45),
            halign='center'
        )
        content.add_widget(amount_input)

        popup = Popup(
            title="兑换筹码",
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
            title_size=sp(16)
        )

        def confirm(instance):
            try:
                amount = int(amount_input.text) if amount_input.text else 0
                if amount > 0:
                    chips = amount * self.EXCHANGE_RATE
                    self.balance += chips
                    self.update_balance_display()
                    self.sound_manager.play("bet")
                    self.show_message(f"✅ 成功充值 {chips} 筹码！")
                    popup.dismiss()
            except ValueError:
                pass

        confirm_btn = Button(
            text="✅ 确认",
            size_hint_y=None,
            height=dp(45),
            background_color=get_color_from_hex('#27ae60'),
            on_press=confirm
        )
        content.add_widget(confirm_btn)

        popup.open()

    def reset_game(self, *args):
        """重置游戏"""
        self.balance = 0
        self.bet = 0
        self.bet_placed = False
        self.spinning = False
        self.update_balance_display()
        self.reset_reels()
        self.bet_input.disabled = False
        self.bet_input.text = ""
        self.spin_btn.disabled = True
        self.spin_btn.background_color = get_color_from_hex('#555555')
        self.bet_btn.disabled = False
        self.bet_btn.background_color = get_color_from_hex('#2980b9')
        self.show_message("游戏已重置，请兑换筹码。")
        Clock.schedule_once(lambda dt: self.show_exchange_dialog(), 0.5)

    def update_balance_display(self):
        """更新余额显示"""
        self.balance_label.text = f"💰 筹码: {self.balance}"

    def show_message(self, message):
        """显示消息"""
        self.message_label.text = message

    def toggle_sound(self, *args):
        """切换音效"""
        enabled = self.sound_manager.toggle_sound()
        self.show_message("🔊 音效已开启" if enabled else "🔇 音效已关闭")

    def quit_game(self, *args):
        """退出游戏"""
        self.sound_manager.stop_bgm()
        App.get_running_app().stop()


class SlotMachineApp(App):
    """老虎机应用"""

    def build(self):
        self.title = "🎰 水果老虎机"

        # 适配不同屏幕尺寸
        if platform == 'android':
            Window.softinput_mode = 'below_target'

        return SlotMachineGame()

    def on_pause(self):
        """应用暂停时"""
        return True

    def on_resume(self):
        """应用恢复时"""
        pass


if __name__ == "__main__":
    SlotMachineApp().run()