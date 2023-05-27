from math import pi as π

import pytest
import torch
from torch import allclose

from flows_on_spheres.transforms.rqspline import (
    _RQSplineTransform,
    RQSplineModule,
)

SAMPLE_SIZE = 100


@pytest.fixture
def angle_inputs():
    θ = torch.empty(SAMPLE_SIZE, 1).uniform_(0, 2 * π)
    return torch.cat([θ.cos(), θ.sin()], dim=1)


@pytest.fixture
def interval_inputs():
    return torch.empty(SAMPLE_SIZE, 1).uniform_(-1, +1)


def test_identity():
    f = _RQSplineTransform(
        torch.ones(SAMPLE_SIZE, 10).cumsum(dim=1),
        torch.ones(SAMPLE_SIZE, 10).cumsum(dim=1),
        torch.ones(SAMPLE_SIZE, 10),
    )
    x = torch.empty(SAMPLE_SIZE, 1).uniform_(1, 10)
    y, ldj = f(x)
    assert allclose(x, y)
    assert allclose(ldj, torch.zeros(1), atol=1e-5)


# Testing RQSplineModule


def test_interval(interval_inputs):
    x = interval_inputs
    transform = RQSplineModule(
        n_segments=4,
        circular=False,
        net_hidden_shape=None,
        net_activation=None,
    )
    y, ldj = transform(None)(x)


def test_inverse(interval_inputs):
    x = interval_inputs
    transform = RQSplineModule(
        n_segments=4,
        circular=False,
        net_hidden_shape=None,
        net_activation=None,
    )
    f = transform(None)
    y, ldj = f(x)
    z, ldj_inv = f.inverse(y)
    assert allclose(x, z, atol=1e-5)
    assert allclose(ldj + ldj_inv, torch.zeros(1), atol=1e-5)


def test_circular(angle_inputs):
    x = angle_inputs
    transform = RQSplineModule(
        n_segments=4,
        circular=True,
        net_hidden_shape=None,
        net_activation=None,
    )
    y, ldj = transform(None)(x)


def test_conditional(interval_inputs):
    x = interval_inputs
    transform = RQSplineModule(
        n_segments=4,
        circular=False,
        net_hidden_shape=[],
        net_activation=None,
    )
    y, ldj = transform(torch.rand_like(x))(x)
