"""The demo site serves the three screens and refuses to invent model output."""

import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.server import Handler
from model_origin.demo import (
    classification_label,
    client_boot,
    load_demo_config,
    load_report,
    run_pair,
    summarize_prompt,
    weights_present,
)

ROOT = Path(__file__).resolve().parents[1]


def test_summarize_prompt_matches_the_notebook_wrapper():
    prompt = summarize_prompt("Короткий текст статті.", "Нічний трамвай")

    assert prompt.startswith("Підсумуй цю статтю:\n ")
    assert "Назва: Нічний трамвай\n " in prompt
    assert prompt.endswith("Текст статті: \nКороткий текст статті.\n ")


def test_summarize_prompt_without_a_title_skips_the_heading():
    prompt = summarize_prompt("Лише текст.")

    assert "Назва:" not in prompt
    assert "Текст статті: \nЛише текст.\n " in prompt


def test_summarize_prompt_stops_at_three_thousand_characters():
    prompt = summarize_prompt("а" * 4000)

    body = prompt.split("Текст статті: \n", 1)[1]
    assert body == ("а" * 3000) + "\n "


def test_classification_label_uses_the_design_wording():
    assert classification_label(0, {0: "NEGATIVE"}) == "0 (negative review)"
    assert classification_label(1, {"1": "POSITIVE"}) == "1 (positive review)"


def test_default_model_directories():
    config = load_demo_config()

    assert config.bert.compressed == ROOT / "models" / "tiny-bert-best"
    assert config.bert.base == ROOT / "models" / "bert-base-sst2-teacher"
    assert config.qwen.compressed == ROOT / "models" / "gkd-qwen2-0.5b-xlsum"
    assert config.qwen.base == ROOT / "models" / "qwen2-1.5b-teacher"


def test_report_rows_differ_by_pair():
    report = load_report()

    assert [row["name"] for row in report["bert"]] == ["Loss", "Accuracy"]
    assert report["bert"][0]["compressed"] == "0.9804"
    assert report["bert"][1]["compressed"] == "0.8291"
    assert report["bert"][0]["base"] == "—"
    assert [row["name"] for row in report["qwen"]] == ["RaugeL"]
    assert report["qwen"][0]["base"] == "—"
    assert report["qwen"][0]["compressed"] == "—"


def test_a_readme_is_not_a_weight_folder(tmp_path):
    folder = tmp_path / "student"
    folder.mkdir()
    (folder / "README.md").write_text("card", encoding="utf-8")

    assert weights_present(folder) is False


def test_config_and_a_weight_file_count_as_weights(tmp_path):
    folder = tmp_path / "student"
    folder.mkdir()
    (folder / "config.json").write_text("{}", encoding="utf-8")
    (folder / "model.safetensors").write_bytes(b"")

    assert weights_present(folder) is True


def test_missing_weights_are_a_message(tmp_path):
    config = load_demo_config()
    empty = config.__class__(
        bert=config.bert.__class__(tmp_path / "teacher", tmp_path / "student"),
        qwen=config.qwen,
        metrics=config.metrics,
        max_new_tokens=config.max_new_tokens,
        max_prompt_tokens=config.max_prompt_tokens,
    )

    result = run_pair("bert", "a gloomy movie", config=empty)

    assert result["base"] is None
    assert result["error"]
    assert "teacher" in result["error"]
    assert "Traceback" not in result["error"]


def test_pages_and_the_unwired_send_path():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        home = _get(httpd, "/")
        methods = _get(httpd, "/methods")
        distillation = _get(httpd, "/method/distillation")
        pruning = _get(httpd, "/method/pruning")
        cat = _get_bytes(httpd, "/static/img/cat-distill.png")

        assert "Zero Cycles" in home
        assert "cat-iia.png" in home
        assert "Demo" in methods
        assert "Pruning" in methods and "Distillation" in methods
        assert "BERT" in distillation and "Qwen" in distillation
        assert "Зимовий ярмарок у Львові" in distillation
        assert "Qwen" not in pruning
        assert "Pruning" in pruning
        assert cat.startswith(b"\x89PNG")

        empty = _post(httpd, {"pair": "bert", "text": "   "})
        assert empty["error"] == "Enter a prompt first."
        status, _ = _post_raw(httpd, {"pair": "other", "text": "x"})
        assert status == 400
    finally:
        httpd.shutdown()
        thread.join(timeout=2)


def test_distillation_boot_switches_examples_and_metrics():
    boot = client_boot("distillation")
    stub = client_boot("quantization")

    assert boot["wired"] is True
    assert set(boot["pairs"]) == {"bert", "qwen"}
    assert boot["metrics"]["bert"][0]["name"] == "Loss"
    assert stub["wired"] is False
    assert list(stub["pairs"]) == ["quantization"]


def _get_bytes(httpd, path: str) -> bytes:
    port = httpd.server_address[1]
    with urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as response:
        assert response.status == 200
        return response.read()


def _get(httpd, path: str) -> str:
    port = httpd.server_address[1]
    with urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as response:
        assert response.status == 200
        return response.read().decode("utf-8", errors="surrogateescape")


def _post(httpd, payload: dict) -> dict:
    status, body = _post_raw(httpd, payload)
    assert status == 200
    return json.loads(body)


def _post_raw(httpd, payload: dict):
    port = httpd.server_address[1]
    request = Request(
        f"http://127.0.0.1:{port}/api/infer",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
