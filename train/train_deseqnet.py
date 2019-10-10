#-*- coding = utf-8 -*-
"""
# Copyright (c) 2018-2019, Shrowshoo-Young All Right Reserved.
#
# This programme is developed as free software for the investigation of human
# pose estimation using RF signals. Redistribution or modification of it is
# allowed under the terms of the GNU General Public Licence published by the
# Free Software Foundation, either version 3 or later version.
#
# Redistribution and use in source or executable programme, with or without
# modification is permitted provided that the following conditions are met:
#
# 1. Redistribution in the form of source code with the copyright notice
#    above, the conditions and following disclaimer retained.
#
# 2. Redistribution in the form of executable programme must reproduce the
#    copyright notice, conditions and following disclaimer in the
#    documentation and\or other literal materials provided in the distribution.
#
# This is an unoptimized software designed to meet the requirements of the
# processing pipeline. No further technical support is guaranteed.
"""

##################################################################################
#                               train_deseqnet.py
#
#   Training procedure of deseqnet.
#
#   Shrowshoo-Young 2019-2, shaoshuyangseu@gmail.com
#   South East University, Vision and Cognition Laboratory, 211189 Nanjing, China
##################################################################################

import torch
import argparse
import os
import time
import numpy as np
import torch.optim as optim
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.utils.data import DataLoader
from torch.autograd import Variable
from torch.autograd import grad
from src.model.deseqnet import DeSeqNetProj, DeSeqNetTest
from src.dataset import deSeqNetLoader
from src.utils import logger, imwrite

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100, help="number of epochs")
    parser.add_argument("--batch_size", type=int, default=1, help="size of each image batch")
    parser.add_argument('--data_path', type=str, default="F:/captest", help="directory of dataset")
    parser.add_argument("--gradient_accumulations", type=int, default=2, help="number of gradient accums before step")
    parser.add_argument("--pretrained_weights", type=str, default="checkpoints/deseqnettest.pth", help="if specified starts from checkpoint model")
    parser.add_argument("--n_cpu", type=int, default=8, help="number of cpu threads to use during batch generation")
    parser.add_argument("--checkpoint_interval", type=int, default=10, help="interval between saving model weights")
    parser.add_argument("--evaluation_interval", type=int, default=1, help="interval evaluations on validation set")
    parser.add_argument("--compute_map", default=False, help="if True computes mAP every tenth batch")
    parser.add_argument("--multiscale_training", default=True, help="allow for multi-scale training")
    opt = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    os.makedirs("output", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)
    with open(os.path.join(opt.data_path, 'keypoint.names'), 'r') as namefile:
        keypointnames = namefile.readlines()
        keypointnames = [line.rstrip() for line in keypointnames]

    logger = logger('logger.txt')
    logger_tag = keypointnames.copy()
    logger_tag.append('total')
    logger.set_tags(logger_tag)

    # Initiate model
    model = DeSeqNetTest().to(device)
    lossfunc = nn.MSELoss()
    if torch.cuda.is_available():
        lossfunc = lossfunc.cuda()

    # If specified we start from checkpoint
    if opt.pretrained_weights:
        model.load_state_dict(torch.load(opt.pretrained_weights))

    # Get dataloader
    dataset = deSeqNetLoader(opt.data_path)
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=opt.batch_size,
        shuffle=False,
        num_workers=opt.n_cpu,
        pin_memory=True,
    )

    # Define optimizer
    optimizer = torch.optim.Adam(model.parameters())

    for epoch in range(opt.epochs):
        model.train()
        start_time = time.time()
        for batch_i, (targets, signal) in enumerate(dataloader):
            batches_done = len(dataloader) * epoch + batch_i

            signal = Variable(signal.to(device))
            targets = Variable(targets.to(device), requires_grad=False)

            outputs = model(signal)
            losses = []
            accum_loss = 0
            # ----------------
            #   Train and Log progress
            # ----------------
            log_str = "[Epoch %d/%d, Batch %d/%d]" % (epoch, opt.epochs, batch_i, len(dataloader))

            for keypoint_i, name in enumerate(keypointnames):
                loss = lossfunc(outputs[:, keypoint_i, :, :], targets[:, keypoint_i, :, :])
                losses.append(loss.item())
                log_str += "[%s: %f]" % (name, loss)
                accum_loss = accum_loss + loss

            losses.append(accum_loss.item())
            logger.append(losses)
            log_str += "[total: %f]\n" % accum_loss
            print(log_str)
            accum_loss.backward()

            optimizer.step()
            optimizer.zero_grad()

        # Validation progress
        # if epoch % opt.evaluation_interval == 0:
        #     print("\n---- Evaluating Model ----")
        #     # Evaluate the model on the validation set
        #     precision, recall, AP, f1, ap_class = evaluate(
        #         model,
        #         path=valid_path,
        #         iou_thres=0.5,
        #         conf_thres=0.5,
        #         nms_thres=0.5,
        #         img_size=opt.img_size,
        #         batch_size=8,
        #     )
        #     evaluation_metrics = [
        #         ("val_precision", precision.mean()),
        #         ("val_recall", recall.mean()),
        #         ("val_mAP", AP.mean()),
        #         ("val_f1", f1.mean()),
        #     ]
        #     logger.list_of_scalars_summary(evaluation_metrics, epoch)

        #    # Print class APs and mAP
        #    ap_table = [["Index", "Class name", "AP"]]
        #    for i, c in enumerate(ap_class):
        #        ap_table += [[c, class_names[c], "%.5f" % AP[i]]]
        #    print(AsciiTable(ap_table).table)
        #    print(f"---- mAP {AP.mean()}")

        if epoch % opt.checkpoint_interval == 0:
            torch.save(model.state_dict(), f"checkpoints/deseqnettest_%d.pth" % epoch)

    logger.close()