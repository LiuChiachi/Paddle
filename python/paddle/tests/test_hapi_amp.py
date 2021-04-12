# copyright (c) 2020 paddlepaddle authors. all rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import division
from __future__ import print_function

import unittest

import numpy as np

import paddle
from paddle import fluid

from paddle import Model
from paddle.static import InputSpec
from paddle.nn.layer.loss import CrossEntropyLoss
from paddle.vision.models import LeNet


@unittest.skipIf(not fluid.is_compiled_with_cuda(),
                 'CPU testing is not supported')
class TestDistTraningUsingAMP(unittest.TestCase):
    def test_amp_training(self):
        for dynamic in [True, False]:
            amp_level = "O1"
            if not fluid.is_compiled_with_cuda():
                self.skipTest('module not tested when ONLY_CPU compling')
            paddle.enable_static() if not dynamic else None
            device = paddle.set_device('gpu')
            net = LeNet()
            inputs = InputSpec([None, 1, 28, 28], "float32", 'x')
            label = InputSpec([None, 1], "int64", "y")
            model = Model(net, inputs, label)
            optim = paddle.optimizer.Adam(
                learning_rate=0.001, parameters=model.parameters())
            amp_configs = {"level": amp_level}
            model.prepare(
                optimizer=optim,
                loss=CrossEntropyLoss(reduction="sum"),
                amp_configs=amp_configs)

    def test_check_input_error(self):
        paddle.disable_static()
        amp_configs_list = [
            {
                "level": "O3"
            },
            {
                "level": "O1",
                "test": 0
            },
            {
                "level": "O1",
                "use_fp16_guard": True
            },
            "O3",
        ]
        if not fluid.is_compiled_with_cuda():
            self.skipTest('module not tested when ONLY_CPU compling')
        device = paddle.set_device('gpu')
        net = LeNet()
        model = Model(net)
        optim = paddle.optimizer.Adam(
            learning_rate=0.001, parameters=model.parameters())
        loss = CrossEntropyLoss(reduction="sum")
        with self.assertRaises(ValueError):
            for i in range(len(amp_configs_list)):
                model.prepare(
                    optimizer=optim, loss=loss, amp_configs=amp_configs_list[i])
        model.prepare(optimizer=optim, loss=loss, amp_configs="O2")


if __name__ == '__main__':
    unittest.main()
