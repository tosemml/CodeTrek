from __future__ import print_function, division

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F

from tqdm import tqdm
import numpy as np
import random
import torch.optim as optim
from sklearn.metrics import roc_auc_score

from dbwalk.data_util.dataset import ProgDict
from dbwalk.ggnn.data_util.graph_dataset import AstGraphDataset
from dbwalk.common.configs import cmd_args, set_device

from dbwalk.ggnn.graphnet.graph_embed import get_gnn
from dbwalk.training.train import train_loop


class GnnBinary(nn.Module):
    def __init__(self, args, prog_dict):
        super(GnnBinary, self).__init__()
        self.gnn = get_gnn(args, len(prog_dict.node_types), len(prog_dict.edge_types))
        self.out_classifier = nn.Linear(args.latent_dim * 2, 1)

    def forward(self, graph_list, label=None):
        node_sel = []
        offset = 0
        for g in graph_list:
            node_sel.append(g.target_idx)
            offset += g.num_nodes
        graph_embed, (_, node_embed) = self.gnn(graph_list)
        target_embed = node_embed[node_sel]
        logits = self.out_classifier(torch.cat([graph_embed, target_embed], dim=1))
        prob = torch.sigmoid(logits)
        if label is not None:
            label = label.to(prob).view(prob.shape)
            loss = -label * torch.log(prob + 1e-18) - (1 - label) * torch.log(1 - prob + 1e-18)
            return torch.mean(loss)
        else:
            return prob


def eval_dataset(model, phase, eval_loader):
    true_labels = []
    pred_probs = []
    model.eval()
    pbar = tqdm(eval_loader)
    for graph_list, label in pbar:
        with torch.no_grad():
            pred = model(graph_list).data.cpu().numpy()
            pred_probs += pred.flatten().tolist()
            true_labels += label.data.numpy().flatten().tolist()
        pbar.set_description('evaluating %s' % phase)
    roc_auc = roc_auc_score(true_labels, pred_probs)
    pred_label = np.where(np.array(pred_probs) > 0.5, 1, 0)
    acc = np.mean(pred_label == np.array(true_labels, dtype=pred_label.dtype))
    print('%s auc: %.4f, acc: %.4f' % (phase, roc_auc, acc))
    return roc_auc


def gnn_arg_constructor(nn_args):
    graph_list, label = nn_args
    return {'graph_list': graph_list, 'label': label.to(cmd_args.device)}


if __name__ == '__main__':
    set_device(cmd_args.gpu)
    np.random.seed(cmd_args.seed)
    random.seed(cmd_args.seed)
    torch.manual_seed(cmd_args.seed)
    prog_dict = ProgDict(cmd_args.data_dir)

    model = GnnBinary(cmd_args, prog_dict).to(cmd_args.device)
    if cmd_args.phase == 'eval': 
        db_eval = AstGraphDataset(cmd_args, prog_dict, cmd_args.data_dir, 'eval')
        eval_loader = db_eval.get_test_loader(cmd_args)
        assert cmd_args.model_dump is not None
        model_dump = os.path.join(cmd_args.save_dir, cmd_args.model_dump)
        print('loading model from', model_dump)
        model.load_state_dict(torch.load(model_dump, map_location=cmd_args.device))    
        eval_dataset(model, 'eval', eval_loader)
        sys.exit()

    db_dev = AstGraphDataset(cmd_args, prog_dict, cmd_args.data_dir, 'dev')
    db_train = AstGraphDataset(cmd_args, prog_dict, cmd_args.data_dir, 'train')
    train_loop(prog_dict, model, db_train, db_dev, eval_dataset,
               nn_arg_constructor=gnn_arg_constructor)
