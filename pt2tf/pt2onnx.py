import torch
from efficientnet_pytorch import EfficientNet

# Specify which model to use
model_name = 'efficientnet-b3'
image_size = EfficientNet.get_image_size(model_name)
print('Image size: ', image_size)

# Load model
model = EfficientNet.from_pretrained(model_name)
model.set_swish(memory_efficient=False)
model.eval()
print('Model image size: ', model._global_params.image_size)

# Dummy input for ONNX
dummy_input = torch.randn(1, 3, 300, 300)

# Export with ONNX
torch.onnx.export(model, dummy_input, f"{model_name}.onnx", verbose=True)
