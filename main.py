"""同声传译 MVP：麦克风 -> ASR -> MT -> TTS。

默认固定时长录音段（每段 4 秒）循环处理，适合快速验证。
后续可替换为 VAD 流式检测以降低延迟。
"""
import sys
import signal
import time
import numpy as np
import sounddevice as sd

from src.asr import ASR
from src.mt import MT
from src.tts import TTS

SAMPLE_RATE = 16000
SEGMENT_SEC = 4          # 每段录音时长（秒）
RMS_THRESHOLD = 0.01     # 低于此能量判定为静默，跳过

running = True


def stop(signum, frame):
    global running
    running = False


def main():
    global running
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print("初始化 ASR (faster-whisper base/int8) ...")
    asr = ASR(model_size="base", device="auto", compute_type="int8")
    print("初始化 MT (stub) ...")
    mt = MT()
    print("初始化 TTS (pyttsx3/espeak-ng 中文) ...")
    tts = TTS(rate=180)

    print("\n=== 日语 / 英语 -> 中文 同声传译 MVP ===")
    f"每段录音 {SEGMENT_SEC}s，Ctrl+C 退出\n"

    seg_idx = 0
    try:
        while running:
            seg_idx += 1
            print(f"[第{seg_idx}段] 录音 {SEGMENT_SEC}s ...", flush=True)
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
                print("   (静默，跳过)\n")
                continue

            text, lang = asr.transcribe(audio, SAMPLE_RATE)
            if not text:
                print("   (ASR 无文本)\n")
                continue
            print(f"   [{lang or '?'}] {text}")

            zh = mt.translate(text, lang)
            print(f"   [中文] {zh}")

            tts.speak(zh)
            print()
    except KeyboardInterrupt:
        pass
    finally:
        print("已退出。")


if __name__ == "__main__":
    main()
