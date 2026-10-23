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
- Loss: 0.9804
- Accuracy: 0.8291

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 0.00027423186148808275
- train_batch_size: 128
- eval_batch_size: 128
- seed: 33
- optimizer: Use OptimizerNames.ADAMW_TORCH_FUSED with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: linear
- num_epochs: 3
- mixed_precision_training: Native AMP

### Training results

| Training Loss | Epoch | Step | Validation Loss | Accuracy |
|:-------------:|:-----:|:----:|:---------------:|:--------:|
| 0.8277        | 1.0   | 527  | 0.9049          | 0.8291   |
| 0.4147        | 2.0   | 1054 | 0.9307          | 0.8326   |
| 0.3132        | 3.0   | 1581 | 0.9804          | 0.8291   |


### Framework versions

- Transformers 5.20.2
- Pytorch 2.14.1+cu130
- Datasets 5.1.0
- Tokenizers 0.23.3
