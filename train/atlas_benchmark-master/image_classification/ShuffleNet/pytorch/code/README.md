# ImageNet training in PyTorch

This implements training of ShuffleNetV2 on the ImageNet dataset, mainly modified from [pytorch/examples](https://github.com/pytorch/examples/tree/master/imagenet).

## ShuffleNet Detail
As of the current date, Ascend-Pytorch is still inefficient for contiguous operations. 
Therefore, ShufflenetV2 is re-implemented using semantics such as custom OP. For details, see models/shufflenetv2_wock_op_woct.py .


## Requirements

- Install PyTorch ([pytorch.org](http://pytorch.org))
- `pip install -r requirements.txt`
- Download the ImageNet dataset from http://www.image-net.org/
    - Then, and move validation images to labeled subfolders, using [the following shell script](https://raw.githubusercontent.com/soumith/imagenetloader.torch/master/valprep.sh)

## Training 1p

To train a model, run `main.py` with the desired model architecture and the path to the ImageNet dataset:

```bash
# FP32 training
bash 1p.sh

# O2 training
bash 1p_amp.sh

# FP32 training for 20 epoch experiment
bash 1p_20e.sh

# FP32 training for 20 epoch experiment
bash 1p_20e_amp.sh

```

## Training multi-cards
```bash
# O2 training 2p
# Only Support device-list setting in [[0,1], [2,3], [4,5], [6,7]]
bash 2p_amp_med.sh

# O2 training 4p
# Only Support device-list setting in [[0,1,2,3], [4,5,6,7]]
bash 4p_amp_med.sh

# O2 training 8p
bash 8p_amp_med.sh

```

## ShufflenetV2 training result

| Acc@1    | FPS       | Npu_nums| Epochs   | Type     |
| :------: | :------:  | :------ | :------: | :------: |
| 61.5     | 1200      | 1       | 20       | O2       |
| 68.5     | 2200      | 1       | 240      | O2       |
| 66.3     | 14000     | 1       | 240      | O2       |



