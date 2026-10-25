# models/

`models/*.joblib` is gitignored — model weights don't belong in git. This file explains
where they go instead, and how the code finds them either way.

## Intermediate results
This directory contains the models saved before and after performing Quantization, Pruning and Knowledge Distillation.

### Knowledge Distillation models
- qwen2-1.5b-teacher - Qwen2-1.5B-Instruct original model 
- gkd-qwen2-0.5b-xlsum - Qwen2-0.5B-Instruct model changed after Knowledge Distillation
- bert-base-sst2-teacher - bert-base-uncased-SST-2 original model 
- tiny-bert-best - bert_uncased_L-2_H-128_A-2 model changed after Knowledge Distillation

### Quantization models
- gemma-baseline - gemma-3-270m-it original model 
- gemma-hqq-xlsum - gemma-3-270m-it quantized model

### Pruning models
- gemma-baseline - gemma-3-270m-it original model 
- best_pruned_model - gemma-3-270m-it model after prunning