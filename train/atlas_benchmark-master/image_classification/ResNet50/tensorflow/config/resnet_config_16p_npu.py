

config = {
    'batch_size': 32,
    'train_epochs': 2,
    'data_dir': '/home/imagenet_TF/',
    'epochs_between_evals': 1,
    'dynamic_loss_scale': True,
    'rank_size': 16,
    'max_train_steps': 1000,
    'iterations_per_loop': 100,
    'save_checkpoints_steps': 115200,
}


def resnet50_config():
    config['global_batch_size'] = config['batch_size'] * config['rank_size']
    return config
