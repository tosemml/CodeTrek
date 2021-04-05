#!/bin/bash

data_root=$HOME/data/dataset/dbwalk
data_name=defuse_offline

bsize=32
embed=256
nlayer=2
nhead=4
hidden=512
dropout=0
setenc=deepset
shuffle_var=False

export CUDA_VISIBLE_DEVICES=0

save_dir=$HOME/scratch/results/dbwalk/b-$bsize-emb-$embed-nl-$nlayer-head-$nhead-hid-$hidden-dp-$dropout-set-$setenc-sv-$shuffle_var

if [ ! -e $save_dir ];
then
    mkdir -p $save_dir
fi

python main.py \
    -data_dir $data_root/$data_name \
    -save_dir $save_dir \
    -data $data_name \
    -set_encoder $setenc \
    -online_walk_gen False \
    -shuffle_var $shuffle_var \
    -batch_size $bsize \
    -embed_dim $embed \
    -nhead $nhead \
    -transformer_layers $nlayer \
    -dim_feedforward $hidden \
    -dropout $dropout \
    -iter_per_epoch 1000 \
    -learning_rate 1e-4 \
    -gpu 0 \
    $@
