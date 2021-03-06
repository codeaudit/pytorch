from .optimizer import Optimizer

class Adadelta(Optimizer):
    """Implements Adadelta algorithm.

    It has been proposed in `ADADELTA: An Adaptive Learning Rate Method`_.

    Arguments:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        rho (float, optional): coefficient used for computing a running average
            of squared gradients (default: 0.9)
        eps (float, optional): term added to the denominator to improve
            numerical stability (default: 1e-6)
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0)

    .. _ADADELTA\: An Adaptive Learning Rate Method:
        https://arxiv.org/abs/1609.05158
    """

    def __init__(self, params, rho=0.9, eps=1e-6, weight_decay=0):
        defaults = dict(rho=rho, eps=eps, weight_decay=weight_decay)
        super(Adadelta, self).__init__(params, defaults)

    def step(self, closure=None):
        """Performs a single optimization step.

        Arguments:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                grad = p.grad.data
                state = self.state[id(p)]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['square_avg'] = grad.new().resize_as_(grad).zero_()
                    state['acc_delta'] = grad.new().resize_as_(grad).zero_()

                square_avg, acc_delta = state['square_avg'], state['acc_delta']
                rho, eps = group['rho'], group['eps']

                state['step'] += 1

                if group['weight_decay'] != 0:
                    grad = grad.add(group['weight_decay'], p.data)

                square_avg.mul_(rho).addcmul_(1 - rho, grad, grad)
                std = square_avg.add(eps).sqrt_()
                delta = acc_delta.add(eps).sqrt_().div_(std).mul_(grad)
                p.data.sub_(delta)
                acc_delta.mul_(rho).addcmul_(1 - rho, delta, delta)

        return loss

