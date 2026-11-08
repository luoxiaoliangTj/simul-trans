"""同声传译 MVP：Kivy GUI 版本（桌面 + Android 双平台）。

桌面端（linux/windows/macOS）：使用 src/asr (faster-whisper)、src/mt (Opus-MT)、
src/tts (pyttsx3) + sounddevice 录音，完整 ASR -> MT -> TTS 闭环。

Android 端：界面可用；ASR/MT/TTS 按平台降级，避免 PortAudio/pyttsx3 在 Android
上不可用导致崩溃，避免 faster-whisper/transformers 这类重 C 扩展依赖被打入 APK
导致 buildozer 构建失败。后续可用 pyjnius 接入 Android 原生 AudioRecord /
TextToSpeech / 离线 ASR。

入口：buildozer 直接打包 main.py，src/ 下的 .py 会随 source.include_exts 被打包，
但仅在桌面平台被导入（见 _init_backend 的平台分支）。
"""

import os
import sys
import time
import threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform as kivy_platform


class SimulTransApp(App):
    """同声传译主应用。"""

    def build(self):
        self.title = "simul-trans"
        self.running = False
        self.thread = None
        self.asr = None
        self.mt = None
        self.tts = None

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        self.status_label = Label(text="就绪", size_hint_y=None, height=36)
        root.add_widget(self.status_label)

        root.add_widget(Label(text="源语言文本", size_hint_y=None, height=26))
        self.src_text = TextInput(text="", readonly=True, size_hint_y=None, height=110)
        root.add_widget(self.src_text)

        root.add_widget(Label(text="中文翻译", size_hint_y=None, height=26))
        self.zh_text = TextInput(text="", readonly=True, size_hint_y=None, height=110)
        root.add_widget(self.zh_text)

        root.add_widget(Label(text="日志", size_hint_y=None, height=26))
        self.log_text = TextInput(text="", readonly=True, size_hint_y=1)
        root.add_widget(self.log_text)

        btn_layout = BoxLayout(size_hint_y=None, height=48, spacing=10)
        self.start_btn = Button(text="开始", on_press=self.toggle)
        btn_layout.add_widget(self.start_btn)
        clear_btn = Button(text="清空", on_press=self.clear)
        btn_layout.add_widget(clear_btn)
        root.add_widget(btn_layout)

        self.log("simul-trans 已就绪（平台：{}）".format(kivy_platform))
        return root

    # ------------------------------------------------------------------ UI
    def log(self, msg):
        """在主线程安全地追加日志。"""

        def _append(dt):
            self.log_text.text += msg + "\n"

        Clock.schedule_once(_append, 0)

    def set_status(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.status_label, "text", msg), 0)

    def set_src(self, text):
        Clock.schedule_once(lambda dt: setattr(self.src_text, "text", text), 0)

    def set_zh(self, text):
        Clock.schedule_once(lambda dt: setattr(self.zh_text, "text", text), 0)

    def toggle(self, instance):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        self.running = True
        self.start_btn.text = "停止"
        self.log("开始同声传译 ...")
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.start_btn.text = "开始"
        self.log("已停止。")

    def clear(self, instance):
        self.src_text.text = ""
        self.zh_text.text = ""
        self.log_text.text = ""
        self.log("已清空。")

    # ---------------------------------------------------------------- backend
    def _init_backend(self):
        plat = kivy_platform
        if plat in ("android", "ios"):
            self.log("移动端后端：使用平台原生 API（当前为界面演示占位）")
            self.log("提示：后续可用 pyjnius 接入 Android AudioRecord / TextToSpeech")
        else:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from src.asr import ASR   # noqa: WPS433 (desktop-only import)
            from src.mt import MT     # noqa: WPS433
            from src.tts import TTS   # noqa: WPS433
            self.asr = ASR(model_size="base", device="auto", compute_type="int8")
            self.mt = MT()
            self.tts = TTS(rate=180)
            self.log("桌面后端：faster-whisper + Opus-MT + pyttsx3 已就绪")

    # ---------------------------------------------------------------- main loop
    def _loop(self):
        try:
            self._init_backend()
        except Exception as e:  # noqa: BLE001
            self.log("后端初始化失败：{}".format(e))
            self.running = False
            Clock.schedule_once(lambda dt: setattr(self.start_btn, "text", "开始"), 0)
            return

        seg_idx = 0
        while self.running:
            seg_idx += 1
            self.log("[第{}段] 处理中 ...".format(seg_idx))
            self.set_status("处理中")

            plat = kivy_platform
            if plat in ("android", "ios"):
                # Android 下暂不做真实录音/ASR，避免 PortAudio 崩溃
                time.sleep(2)
                self.set_src("[移动端演示：未接入麦克风]")
                self.set_zh("[移动端演示：待接入 Android 原生 ASR/MT]")
            else:
                import numpy as np   # noqa: WPS433 (desktop-only)
                import sounddevice as sd  # noqa: WPS433 (desktop-only)

                SAMPLE_RATE = 16000
                SEGMENT_SEC = 4
                RMS_THRESHOLD = 0.01

                audio = sd.rec(
                    int(SEGMENT_SEC * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype="float32",
                )
                sd.wait()
                audio = audio.flatten()
                rms = float(np.sqrt(np.mean(audio ** 2)))
                if rms < RMS_THRESHOLD:
                    self.log("   (静默，跳过)")
                    self.set_status("就绪")
                    continue

                text, lang = self.asr.transcribe(audio, SAMPLE_RATE)
                if not text:
                    self.log("   (ASR 无文本)")
                    self.set_status("就绪")
                    continue
                self.log("   [{}] {}".format(lang or "?", text))
                self.set_src("[{}] {}".format(lang or "?", text))

                zh = self.mt.translate(text, lang)
                self.log("   [中文] {}".format(zh))
                self.set_zh(zh)

                self.tts.speak(zh)

            self.set_status("就绪")
            if self.running:
                time.sleep(1)

        self.log("循环结束。")

    def on_pause(self):
        """Kivy Android 生命周期：应用进入后台时返回 True 允许暂停。"""
        return True

    def on_resume(self):
        """Kivy Android 生命周期：从后台恢复。"""
        pass


if __name__ == "__main__":
    SimulTransApp().run()
