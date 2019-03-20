# coding=utf8
from __future__ import absolute_import, division, print_function

import sys
import numpy as np
import pickle as pkl
import caffe

# deploy文件
MODEL_FILE = 'SfSNet_deploy.prototxt'
# 预先训练好的caffe模型
PRETRAIN_FILE = 'SfSNet.caffemodel.h5'


def reverse(arr):
    """
    :type arr: np.ndarray
    """
    indices = list(np.arange(arr.shape[0]-1, -1, -1))
    return arr[indices]


if __name__ == '__main__':
    # 让caffe以测试模式读取网络参数
    net = caffe.Net(MODEL_FILE, PRETRAIN_FILE, caffe.TEST)
    print('*' * 80)
    name_weights = {}
    print(len(net.params.keys()))
    keys = open('keys.txt', 'w')
    keys.write('generated by wow/convert_to_pkl.py\n\n')
    # 遍历每一层
    for param_name in net.params.keys():
        name_weights[param_name] = {}
        layer_params = net.params[param_name]
        if len(layer_params) == 1:  # 反卷积层
            # 权重参数
            weight = layer_params[0].data
            name_weights[param_name]['weight'] = weight

            print('%s:\n\t%s (weight)' % (param_name, weight.shape))
            keys.write('%s:\n\t%s (weight)\n' % (param_name, weight.shape))
        elif len(layer_params) == 2:  # 卷积层
            # 权重参数
            weight = layer_params[0].data
            name_weights[param_name]['weight'] = weight
            # 偏置参数
            bias = layer_params[1].data
            name_weights[param_name]['bias'] = bias

            print('%s:\n\t%s (weight)' % (param_name, weight.shape))
            print('\t%s (bias)' % str(bias.shape))
            keys.write('%s:\n\t%s (weight)\n' % (param_name, weight.shape))
            keys.write('\t%s (bias)\n' % str(bias.shape))
        elif len(layer_params) == 3:  # BatchNorm
            # running_mean
            running_mean = layer_params[0].data
            name_weights[param_name]['running_mean'] = running_mean / layer_params[2].data
            # running_var
            running_var = layer_params[1].data
            name_weights[param_name]['running_var'] = running_var/layer_params[2].data

            print('%s:\n\t%s (running_var)' % (param_name, running_var.shape),)
            print('\t%s (running_mean)' % str(running_mean.shape))
            keys.write('%s:\n\t%s (running_var)\n' % (param_name, running_var.shape))
            keys.write('\t%s (running_mean)\n' % str(running_mean.shape))
    keys.close()
    with open('weights.pkl', 'wb') as f:
        pkl.dump(name_weights, f, protocol=2)
