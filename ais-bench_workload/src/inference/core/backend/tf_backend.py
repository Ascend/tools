

import tensorflow as tf
from tensorflow.core.framework import graph_pb2
import cv2
import numpy as np
from backendbase import BackendBase

class BackendTensorflow(BackendBase):
    def __init__(self, batchsize):
        super(BackendTensorflow, self).__init__(batchsize)
        

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "tensorflow"

    def image_format(self):
        # By default tensorflow uses NHWC (and the cpu implementation only does NHWC)
        return "NHWC"

    def load(self, model_path, inputs=None, outputs=None):
        # there is no input/output meta data i the graph so it need to come from config.
        if not inputs:
            raise ValueError("BackendTensorflow needs inputs")
        if not outputs:
            raise ValueError("BackendTensorflow needs outputs")
        self.outputs = outputs
        self.inputs = inputs

        # TODO: support checkpoint and saved_model formats?
        graph_def = graph_pb2.GraphDef()
        with open(model_path, "rb") as f:
            graph_def.ParseFromString(f.read())
        g = tf.compat.v1.import_graph_def(graph_def, name='')
        self.sess = tf.compat.v1.Session(graph=g)
        return self

    def predict(self, images):
        feed = {self.inputs[0]: images}
        return self.sess.run(self.outputs, feed_dict=feed)
