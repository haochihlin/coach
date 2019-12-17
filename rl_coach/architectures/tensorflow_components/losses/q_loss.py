#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.losses import Loss, Huber, MeanSquaredError

from rl_coach.architectures.tensorflow_components.losses.head_loss import HeadLoss, LossInputSchema
from rl_coach.architectures.tensorflow_components.losses.head_loss import LOSS_OUT_TYPE_LOSS
from rl_coach.base_parameters import AgentParameters

class QLoss(HeadLoss):
    def __init__(self,
                 network_name: str,
                 head_idx: int,
                 agent_parameters: AgentParameters,
                 loss_type: Loss = MeanSquaredError,
                 loss_weight: float=1.):
        """
        Loss for Q-Value Head.
        :param head_idx: the index of the corresponding head.
        :param loss_type: loss function with default of mean squared error (i.e. L2Loss).
        :param loss_weight: scalar used to adjust relative weight of loss (if using this loss with others).
        """
        super(QLoss, self).__init__(name=network_name)
        self.head_idx = head_idx
        assert (loss_type == MeanSquaredError) or (loss_type == Huber), "Only expecting L2Loss or HuberLoss."
        #self.loss_fn = keras.losses.mean_squared_error
        self.loss_fn = keras.losses.get(loss_type)()
        # sample_weight can be used like https://github.com/keras-team/keras/blob/master/keras/losses.py

    @property
    def input_schema(self) -> LossInputSchema:
        return LossInputSchema(
            model_outputs=['q_value_pred'],
            non_trainable_args=['target']
        )

    def loss_forward(self, q_value_pred, target):
        """
        Used for forward pass through loss computations.
        :param q_value_pred: state-action q-values predicted by QHead network, of shape (batch_size, num_actions).
        :param target: actual state-action q-values, of shape (batch_size, num_actions).
        :return: loss, of shape (batch_size).
        """
        # TODO: preferable to return a tensor containing one loss per instance, rather than returning the mean loss.
        #  This way, Keras can apply class weights or sample weights when requested.
        loss = tf.reduce_mean(self.loss_fn(q_value_pred, target))
        return {LOSS_OUT_TYPE_LOSS: [loss]}