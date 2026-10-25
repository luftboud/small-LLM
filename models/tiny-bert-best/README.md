---
library_name: transformers
license: apache-2.0
base_model: google/bert_uncased_L-2_H-128_A-2
tags:
- generated_from_trainer
metrics:
- accuracy
model-index:
- name: tiny-bert-sst2
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# tiny-bert-sst2

This model is a fine-tuned version of [google/bert_uncased_L-2_H-128_A-2](https://huggingface.co/google/bert_uncased_L-2_H-128_A-2) on the nyu-mll/glue dataset.
It achieves the following results on the evaluation set:
- Loss: 2.1711
- Accuracy: 0.8165

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 0.0008258879417208129
- train_batch_size: 128
- eval_batch_size: 128
- seed: 33
- optimizer: Use OptimizerNames.ADAMW_TORCH_FUSED with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: linear
- num_epochs: 8
- mixed_precision_training: Native AMP

### Training results

| Training Loss | Epoch | Step | Validation Loss | Accuracy |
|:-------------:|:-----:|:----:|:---------------:|:--------:|
| 1.6890        | 1.0   | 474  | 2.0359          | 0.8096   |
| 0.7278        | 2.0   | 948  | 2.2928          | 0.8108   |
| 0.4772        | 3.0   | 1422 | 2.0593          | 0.8119   |
| 0.3505        | 4.0   | 1896 | 2.2381          | 0.8131   |
| 0.2623        | 5.0   | 2370 | 2.3309          | 0.8131   |
| 0.2077        | 6.0   | 2844 | 2.2255          | 0.8119   |
| 0.1655        | 7.0   | 3318 | 2.1711          | 0.8165   |
| 0.1351        | 8.0   | 3792 | 2.1343          | 0.8096   |


### Framework versions

- Transformers 5.20.2
- Pytorch 2.14.0+cu130
- Datasets 5.1.0
- Tokenizers 0.23.3
