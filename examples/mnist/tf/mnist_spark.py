# Copyright 2017 Yahoo Inc.
# Licensed under the terms of the Apache 2.0 license.
# Please see LICENSE file in the project root for terms.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pyspark.context import SparkContext
from pyspark.conf import SparkConf

import argparse
import os
import numpy
import pydoop.hdfs as hdfs
import sys
import tensorflow as tf
import threading
from datetime import datetime

from com.yahoo.ml.tf import TFCluster
import mnist_dist

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--epochs", help="number of epochs", type=int, default=0)
parser.add_argument("-f", "--format", help="example format: (csv|pickle|tfr)", choices=["csv","pickle","tfr"], default="csv")
parser.add_argument("-i", "--images", help="HDFS path to MNIST images in parallelized format")
parser.add_argument("-l", "--labels", help="HDFS path to MNIST labels in parallelized format")
parser.add_argument("-m", "--model", help="HDFS path to save/load model during train/test", default="mnist_model")
parser.add_argument("-o", "--output", help="HDFS path to save test/inference output", default="predictions")
parser.add_argument("-r", "--readers", help="number of reader/enqueue threads", type=int, default=1)
parser.add_argument("-s", "--steps", help="maximum number of steps", type=int, default=1000)
parser.add_argument("-tb", "--tensorboard", help="launch tensorboard process", action="store_true")
parser.add_argument("-X", "--mode", help="train|test", default="train")
parser.add_argument("-c", "--rdma", help="use rdma connection", default=False)
args = parser.parse_args()
print("args:",args)

sc = SparkContext(conf=SparkConf().setAppName("mnist_tf"))

print("{0} ===== Start".format(datetime.now().isoformat()))

num_executors = int(sc._conf.get("spark.executor.instances"))
num_ps = 1
cluster = TFCluster.reserve(sc, num_executors, num_ps, args.tensorboard, TFCluster.InputMode.TENSORFLOW)
cluster.start(mnist_dist.map_fun, args)
cluster.shutdown()

print("{0} ===== Stop".format(datetime.now().isoformat()))
