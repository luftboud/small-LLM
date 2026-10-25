"""Local demo inference for the method pages.

BERT classifies a sentence. Qwen, pruning, and quantization summarize an article.
Weights are read only from the directories in ``config/default.yaml``. A missing
folder is a message, not a download and not a traceback.
"""

from __future__ import annotations

import gc
import json
import re
import threading
from dataclasses import dataclass
from pathlib import Path

import yaml

_LOCK = threading.Lock()
_CACHE: dict[tuple[str, str], tuple[object, object]] = {}
_PROMPT_LIMIT = 3000
_MISSING = "\u2014"

BERT_EXAMPLES = (
    {
        "label": "by far the worst movie of the year",
        "text": "by far the worst movie of the year",
        "title": "",
    },
    {"label": "of saucy", "text": "of saucy", "title": ""},
    {
        "label": "we never feel anything for these characters",
        "text": "we never feel anything for these characters",
        "title": "",
    },
)

QWEN_EXAMPLES = (
    {
        "label": "Зимовий ярмарок у Львові",
        "title": "Зимовий ярмарок у Львові",
        "text": (
            "У Львові на площі Ринок відкрили зимовий ярмарок. "
            "Дерев'яні ятки продають мед, свічки і гарячий узвар. "
            "Увечері площа світиться гірляндами, а на сцені грає капела."
        ),
    },
    {
        "label": "Нічний трамвай",
        "title": "Нічний трамвай",
        "text": (
            "Нічний трамвай у Києві запізнився на дванадцять хвилин. "
            "На зупинці чекали троє пасажирів з термосами. "
            "Водій відчинив двері і вибачився коротко, без оголошення."
        ),
    },
    {
        "label": "Берег Світязя",
        "title": "Берег Світязя",
        "text": (
            "На озері Світязь вода спала після спеки, і берег став ширшим. "
            "Рибалки залишили човни вище, ніж у червні. "
            "До вечора вітер приніс хмари, але дощу так і не було."
        ),
    },
)

GEMMA_PAIRS = ("pruning", "quantization")


@dataclass(frozen=True)
class ModelPaths:
    """Teacher and student directories for one distillation pair."""

    base: Path
    compressed: Path


@dataclass(frozen=True)
class DemoConfig:
    """Paths and generation limits for the local demo."""

    bert: ModelPaths
    qwen: ModelPaths
    pruning: ModelPaths
    quantization: ModelPaths
    metrics: Path
    max_new_tokens: int
    max_prompt_tokens: int


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_demo_config(path: Path | None = None) -> DemoConfig:
    """Read the ``demo`` section. Relative paths are resolved from the repo root."""
    root = repo_root()
    config_path = path or root / "config" / "default.yaml"
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    demo = raw.get("demo") or {}

    def pair(name: str) -> ModelPaths:
        section = demo.get(name) or {}
        return ModelPaths(
            base=_resolve(root, section.get("base", "")),
            compressed=_resolve(root, section.get("compressed", "")),
        )

    return DemoConfig(
        bert=pair("bert"),
        qwen=pair("qwen"),
        pruning=pair("pruning"),
        quantization=pair("quantization"),
        metrics=_resolve(root, demo.get("metrics", "results/demo_metrics.json")),
        max_new_tokens=int(demo.get("max_new_tokens", 128)),
        max_prompt_tokens=int(demo.get("max_prompt_tokens", 960)),
    )


def gemma_prompt(text: str) -> str:
    """Wrap an article the way notebooks 03 and 04 wrap an XLSum record."""
    body = text.replace("\u200e", "")
    body = re.sub(r" {2,}", " ", body).strip()
    return f"Підсумуй цю статтю:\n{body}\n"


def summarize_prompt(text: str, title: str = "") -> str:
    """Wrap an article the way notebook 05 wraps an XLSum record."""
    body = re.sub(r" {2,}", " ", text).strip()[:_PROMPT_LIMIT]
    heading = re.sub(r" {2,}", " ", title).strip()
    prompt = "Підсумуй цю статтю:\n "
    if heading:
        prompt += f"Назва: {heading}\n "
    prompt += f"Текст статті: \n{body}\n "
    return prompt


def classification_label(index: int, id2label: dict | None) -> str:
    """Render a SST-2 class the way the design writes it: ``0 (negative review)``."""
    raw = ""
    if id2label:
        raw = str(id2label.get(index, id2label.get(str(index), "")))
    lowered = raw.lower()
    if "neg" in lowered:
        kind = "negative review"
    elif "pos" in lowered:
        kind = "positive review"
    elif index == 0:
        kind = "negative review"
    elif index == 1:
        kind = "positive review"
    else:
        kind = raw or "unknown"
    return f"{index} ({kind})"


def weights_present(path: Path) -> bool:
    """A folder counts only when it holds a transformers config and weight files."""
    if not path.is_dir():
        return False
    names = {item.name for item in path.iterdir()}
    if "config.json" not in names:
        return False
    return any(
        name == "model.safetensors.index.json"
        or name == "qmodel.pt"
        or name.endswith(".safetensors")
        or name.endswith(".bin")
        for name in names
    )


def display_path(path: Path) -> str:
    try:
        return path.relative_to(repo_root()).as_posix()
    except ValueError:
        return path.as_posix()


def format_report(payload: dict, key: str) -> list[dict[str, str]]:
    rows = (payload.get(key) or {}).get("rows") or []
    formatted = []
    for row in rows:
        formatted.append(
            {
                "name": str(row.get("name", "")),
                "base": _cell(row.get("base")),
                "compressed": _cell(row.get("compressed")),
            }
        )
    return formatted


def load_report(path: Path | None = None) -> dict[str, list[dict[str, str]]]:
    metrics_path = path or load_demo_config().metrics
    if metrics_path.is_file():
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    else:
        payload = {}
    return {
        "bert": format_report(payload, "bert"),
        "qwen": format_report(payload, "qwen"),
        "pruning": format_report(payload, "pruning"),
        "quantization": format_report(payload, "quantization"),
    }


def client_boot(method: str) -> dict:
    """JSON the method page needs: tabs, example chips, and the static report."""
    report = load_report()
    if method == "distillation":
        return {
            "wired": True,
            "pair": "bert",
            "pairs": {
                "bert": {"label": "BERT", "examples": list(BERT_EXAMPLES)},
                "qwen": {"label": "Qwen", "examples": list(QWEN_EXAMPLES)},
            },
            "metrics": report,
        }
    if method in GEMMA_PAIRS:
        return {
            "wired": True,
            "pair": method,
            "pairs": {method: {"label": "Gemma", "examples": list(QWEN_EXAMPLES)}},
            "metrics": {method: report[method]},
        }
    return {
        "wired": False,
        "pair": method,
        "pairs": {},
        "metrics": {},
    }


def run_pair(
    pair_name: str,
    text: str,
    title: str = "",
    config: DemoConfig | None = None,
) -> dict:
    """Run the teacher, then the student. Missing weights never raise."""
    cleaned = text.strip()
    if pair_name not in ("bert", "qwen", *GEMMA_PAIRS):
        return _failure("Choose a model.")
    if not cleaned:
        return _failure("Enter a prompt first.")
    cfg = config or load_demo_config()
    paths = getattr(cfg, pair_name)
    missing = [item for item in (paths.base, paths.compressed) if not weights_present(item)]
    if missing:
        listed = " and ".join(display_path(item) for item in missing)
        return _failure(f"Weights were not found in {listed}.")
    with _LOCK:
        try:
            _keep_pair(pair_name)
            if pair_name == "bert":
                return _run_bert(paths, cleaned)
            if pair_name == "qwen":
                return _run_qwen(paths, cleaned, title, cfg)
            return _run_gemma(paths, cleaned, cfg, quantized=pair_name == "quantization")
        except Exception as exc:  # noqa: BLE001 — the page shows one line, not a traceback
            return _failure(f"The model could not answer: {_short(exc)}")


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _cell(value: object) -> str:
    if value is None or value == "":
        return _MISSING
    return str(value)


def _failure(message: str) -> dict:
    return {"base": None, "compressed": None, "error": message}


def _short(exc: Exception) -> str:
    line = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
    return line[:200]


def _keep_pair(pair_name: str) -> None:
    dropped = [key for key in list(_CACHE) if key[0] != pair_name]
    for key in dropped:
        _CACHE.pop(key, None)
    if not dropped:
        return
    gc.collect()
    try:
        import torch
    except Exception:  # noqa: BLE001
        return
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        torch.mps.empty_cache()


def _device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _dtype(device: str):
    import torch

    if device == "cuda" and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    if device == "cuda":
        return torch.float16
    return torch.float32


def _load(path: Path, device: str, kind: str):
    key = (kind, str(path))
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    if kind == "bert":
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True)
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            path, dtype=_dtype(device), local_files_only=True
        )
    model.to(device)
    model.eval()
    _CACHE[(kind, str(path))] = (model, tokenizer)
    return model, tokenizer


def _run_bert(paths: ModelPaths, text: str) -> dict:
    device = _device()
    base = _load(paths.base, device, "bert")
    compressed = _load(paths.compressed, device, "bert")
    base_text, base_error = _safe(lambda: _predict_class(base, text, device))
    compressed_text, compressed_error = _safe(lambda: _predict_class(compressed, text, device))
    return _joined(base_text, base_error, compressed_text, compressed_error)


def _run_qwen(paths: ModelPaths, text: str, title: str, config: DemoConfig) -> dict:
    device = _device()
    content = summarize_prompt(text, title)
    base = _load(paths.base, device, "qwen")
    compressed = _load(paths.compressed, device, "qwen")
    base_text, base_error = _safe(lambda: _generate(base, content, device, config))
    compressed_text, compressed_error = _safe(
        lambda: _generate(compressed, content, device, config)
    )
    return _joined(base_text, base_error, compressed_text, compressed_error)


def _run_gemma(paths: ModelPaths, text: str, config: DemoConfig, quantized: bool) -> dict:
    device = _device()
    content = gemma_prompt(text)
    kind = "quantization" if quantized else "pruning"
    base = _load(paths.base, device, kind)
    compressed = (
        _load_hqq(paths.compressed, device, kind)
        if quantized
        else _load(paths.compressed, device, kind)
    )
    base_text, base_error = _safe(lambda: _generate(base, content, device, config))
    compressed_text, compressed_error = _safe(
        lambda: _generate(compressed, content, device, config)
    )
    return _joined(base_text, base_error, compressed_text, compressed_error)


def _load_hqq(path: Path, device: str, kind: str):
    """Load a model saved by ``AutoHQQHFModel.save_quantized`` (``qmodel.pt``)."""
    key = (kind, str(path))
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    from hqq.models.hf.base import AutoHQQHFModel
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoHQQHFModel.from_quantized(
        str(path),
        compute_dtype=_dtype(device),
        device=device,
        cache_dir=None,
    )
    model.eval()
    _CACHE[key] = (model, tokenizer)
    return model, tokenizer


def _joined(base_text, base_error, compressed_text, compressed_error) -> dict:
    if base_error and compressed_error:
        return _failure(base_error)
    return {
        "base": base_text if base_error is None else base_error,
        "compressed": compressed_text if compressed_error is None else compressed_error,
        "error": None,
    }


def _safe(fn):
    try:
        return fn(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"The model could not answer: {_short(exc)}"


def _predict_class(bundle, text: str, device: str) -> str:
    import torch

    model, tokenizer = bundle
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
    index = int(logits.argmax(dim=-1).item())
    return classification_label(index, getattr(model.config, "id2label", {}))


def _as_prompt(tokenizer, content: str) -> str:
    if getattr(tokenizer, "chat_template", None):
        messages = [{"role": "user", "content": content}]
        return tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    return content


def _generate(bundle, content: str, device: str, config: DemoConfig) -> str:
    import torch

    model, tokenizer = bundle
    prompt = _as_prompt(tokenizer, content)
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    if inputs["input_ids"].shape[1] > config.max_prompt_tokens:
        inputs = {key: value[:, -config.max_prompt_tokens :] for key, value in inputs.items()}
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=config.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=model.generation_config.eos_token_id,
        )
    new_tokens = output[0, inputs["input_ids"].shape[1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
