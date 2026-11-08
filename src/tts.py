"""TTS 模块：pyttsx3 + espeak-ng 中文语音合成与播放（纯本地，无联网）。"""
import pyttsx3
import threading


class TTS:
    def __init__(self, rate=180, voice_lang_hint="zh"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self._pick_voice(voice_lang_hint)
        self._lock = threading.Lock()

    def _pick_voice(self, lang_hint):
        voices = self.engine.getProperty("voices")
        for v in voices:
            langs = v.languages or []
            if any(lang_hint in str(l).lower() for l in langs):
                self.engine.setProperty("voice", v.id)
                print(f"[TTS] 选用语音: {v.id} ({langs})")
                return
        print(f"[TTS] 未找到 {lang_hint} 语音，使用默认")

    def speak(self, text: str):
        """非阻塞合成播放（独立线程），不阻塞主 ASR 循环。"""
        if not text or "[MT 未就绪]" in text:
            return
        def _run():
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
        threading.Thread(target=_run, daemon=True).start()
