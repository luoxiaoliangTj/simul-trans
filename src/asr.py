"""ASR 模块：faster-whisper 语音识别（日语 / 英语 -> 源语言文本）。

已缓存模型：tiny、base（~/.cache/huggingface/hub/models--Systran--faster-whisper-*）。
同声传译对延迟敏感，默认用 base + int8（CPU 上也够用）；如需更低延迟可切 tiny。
"""
from faster_whisper import WhisperModel
import numpy as np


class ASR:
    def __init__(self, model_size="base", device="auto", compute_type="int8"):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        self.last_lang = None

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000):
        """audio: float32 numpy array, shape (N,), 16kHz mono."""
        if audio.size == 0:
            return "", None
        segments, info = self.model.transcribe(
            audio,
            language=None,      # 自动检测源语言（ja / en / zh 等）
            task="transcribe",
            vad_filter=True,    # 自动剔除静默，只转有语音的段
            beam_size=1,        # 贪心解码，更快
        )
        text = "".join(seg.text for seg in segments).strip()
        self.last_lang = info.language
        return text, info.language
