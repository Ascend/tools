import torch
import torch.nn as nn
import torch.nn.functional as F

g_feat_in = []
g_feat_out = []
g_grad_in = []
g_grad_out = []


def forward_hook_fn(module, input, output):
    g_feat_in.append(input)
    g_feat_out.append(output)
    print(module)
    print(input)
    print(output)


def backward_hook_fn(module, grad_input, grad_output):
    g_grad_in.append(grad_input)
    g_grad_out.append(grad_output)
    print(module)
    print(grad_input)
    print(grad_input)





