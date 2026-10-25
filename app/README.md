# app/

Local site for the Zero Cycles demo. The pages follow the Figma frames: home, method
cards, and a prompt screen. Distillation has BERT and Qwen tabs. Pruning and
quantization each have one Gemma tab.

```bash
source .venv/bin/activate
python app/server.py
```

Opens at http://127.0.0.1:8000. Stop it with `Ctrl+C`.

The site reads weights only from the directories in `config/default.yaml`:

| Role | BERT | Qwen | Gemma pruning | Gemma quantization |
|---|---|---|---|---|
| Base | `models/bert-base-sst2-teacher` | `models/qwen2-1.5b-teacher` | `models/gemma-baseline` | `models/gemma-baseline` |
| Compressed | `models/tiny-bert-best` | `models/gkd-qwen2-0.5b-xlsum` | `models/best_pruned_model` | `models/gemma-hqq-xlsum` |

Each directory needs a transformers `config.json` and a weight file. If a directory is
empty, Send explains that instead of printing a traceback. Loss, accuracy, ROUGE,
size, and parameter counts come from `results/demo_metrics.json` and do not
change with the prompt. Each row compares the base and compressed model saved
for that tab.
