"""MT 模块：基于 HuggingFace Opus-MT 的本地机器翻译（源语言 -> 中文）。

依赖：torch + transformers（已安装 torch 2.15.0+cpu，transformers 4.46.3）。
模型（经 hf-mirror 镜像下载）：
  - en -> zh: Helsinki-NLP/opus-mt-en-zh   (已验证可用)
  - ja -> zh: 无直接模型，回退 ja -> en -> zh 两步
    ja -> en: Helsinki-NLP/opus-mt-jap-en   (待验证)
    en -> zh: 复用上述模型
"""
import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
import threading

MODEL_DIR = os.path.expanduser("~/.simul-trans/mt_models")

# 单步模型：src_lang -> repo_id (目标语言固定为 zh，除非特别标注)
OPUS_MODELS = {
    "en": "Helsinki-NLP/opus-mt-en-zh",      # en -> zh
    "ja": "Helsinki-NLP/opus-mt-jap-zh",     # ja -> zh (不存在，回退两步)
}
# 两步回退：ja -> en 再 en -> zh
JA_FALLBACK = ("Helsinki-NLP/opus-mt-jap-en", "en")  # (repo_id, middle_lang)


class MT:
    def __init__(self, model_dir=MODEL_DIR):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self._lock = threading.Lock()
        self._models = {}   # repo_id -> (tokenizer, model)
        self.ready = True   # 模型懒加载，首次调用自动下载

    def _load(self, repo_id):
        """懒加载指定 repo 的 MarianMT 模型。"""
        if repo_id in self._models:
            return
        import torch
        from transformers import MarianMTModel, MarianTokenizer
        local_dir = os.path.join(self.model_dir, repo_id.replace("/", "--"))
        try:
            tokenizer = MarianTokenizer.from_pretrained(
                local_dir if os.path.exists(os.path.join(local_dir, "config.json"))
                else repo_id,
                cache_dir=self.model_dir,
            )
            model = MarianMTModel.from_pretrained(
                local_dir if os.path.exists(os.path.join(local_dir, "config.json"))
                else repo_id,
                cache_dir=self.model_dir,
            )
            model.eval()
            self._models[repo_id] = (tokenizer, model)
            print(f"[MT] 已加载 {repo_id}")
        except Exception as e:
            print(f"[MT] 加载 {repo_id} 失败: {e}")

    def _run(self, repo_id, text: str) -> str:
        tokenizer, model = self._models[repo_id]
        import torch
        with self._lock:
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                out = model.generate(**inputs, max_length=512)
            result = tokenizer.batch_decode(out, skip_special_tokens=True)[0]
        return result

    def translate(self, text: str, src_lang: str) -> str:
        if not text:
            return ""
        if src_lang == "zh":
            return text  # 已经是中文，无需翻译

        # 尝试直接模型
        repo_id = OPUS_MODELS.get(src_lang)
        if repo_id:
            self._load(repo_id)
            if repo_id in self._models:
                return self._run(repo_id, text)

        # ja -> zh 缺失：回退 ja -> en -> zh
        if src_lang == "ja":
            mid_repo, mid_lang = JA_FALLBACK
            self._load(mid_repo)
            if mid_repo not in self._models:
                return f"[MT 模型缺失] {text}"
            en_text = self._run(mid_repo, text)
            # 再 en -> zh
            zh_repo = OPUS_MODELS["en"]
            self._load(zh_repo)
            if zh_repo not in self._models:
                return f"[MT 模型缺失] {text}"
            return self._run(zh_repo, en_text)

        return f"[MT 模型缺失] {text}"
