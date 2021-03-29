#!/bin/bash

data_root=$HOME/data/dataset/dbwalk/ggnn
data_name=debug_gnn_defuse

lv=5

export CUDA_VISIBLE_DEVICES=1

save_dir=$HOME/scratch/results/dbwalk/ggnn/$data_name/lv-$lv

if [ ! -e $save_dir ];
then
    mkdir -p $save_dir
fi

python main_gnn_defuse.py \
    -data_dir $data_root/$data_name \
    -save_dir $save_dir \
    -batch_size 5 \
    -max_lv $lv \
    -iter_per_epoch 20 \
    -num_proc 0 \
    -gpu 0 \
    $@