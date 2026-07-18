"""NeuralOperator library backbone wrapper.

Provides FNO, DeepONet, and other models from the neuraloperator package.
"""

try:
    from neuralop.models import FNO, DeepONet
    NEURALOPERATOR_AVAILABLE = True
except ImportError:
    NEURALOPERATOR_AVAILABLE = False
    FNO = None
    DeepONet = None


from . import register_backbone


class NeuralOperatorFNO:
    """Wrapper around NeuralOperator FNO."""

    def __init__(self, in_channels: int = 3, out_channels: int = 1, **kwargs):
        if not NEURALOPERATOR_AVAILABLE:
            raise ImportError("neuraloperator package not installed")
        self.model = FNO(in_channels=in_channels, out_channels=out_channels, **kwargs)

    def forward(self, x):
        return self.model(x)

    def __call__(self, x):
        return self.forward(x)


class NeuralOperatorDeepONet:
    """Wrapper around NeuralOperator DeepONet."""

    def __init__(self, branch_net, trunk_net, **kwargs):
        if not NEURALOPERATOR_AVAILABLE:
            raise ImportError("neuraloperator package not installed")
        self.model = DeepONet(branch_net=branch_net, trunk_net=trunk_net, **kwargs)

    def forward(self, x):
        return self.model(x)

    def __call__(self, x):
        return self.forward(x)


# Auto-register
if NEURALOPERATOR_AVAILABLE:
    register_backbone("fno", NeuralOperatorFNO)
    register_backbone("deeponet", NeuralOperatorDeepONet)
