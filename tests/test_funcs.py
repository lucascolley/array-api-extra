from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

# array-api-strict#6
import array_api_strict as xp  # type: ignore[import-untyped]
import pytest
from numpy.testing import assert_array_equal, assert_equal

from array_api_extra import atleast_nd, expand_dims, kron

if TYPE_CHECKING:
    Array = Any  # To be changed to a Protocol later (see array-api#589)


class TestAtLeastND:
    def test_0D(self):
        x = xp.asarray(1)

        y = atleast_nd(x, ndim=0, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=1, xp=xp)
        assert_array_equal(y, xp.ones((1,)))

        y = atleast_nd(x, ndim=5, xp=xp)
        assert_array_equal(y, xp.ones((1, 1, 1, 1, 1)))

    def test_1D(self):
        x = xp.asarray([0, 1])

        y = atleast_nd(x, ndim=0, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=1, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=2, xp=xp)
        assert_array_equal(y, xp.asarray([[0, 1]]))

        y = atleast_nd(x, ndim=5, xp=xp)
        assert_array_equal(y, xp.reshape(xp.arange(2), (1, 1, 1, 1, 2)))

    def test_2D(self):
        x = xp.asarray([[3]])

        y = atleast_nd(x, ndim=0, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=2, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=3, xp=xp)
        assert_array_equal(y, 3 * xp.ones((1, 1, 1)))

        y = atleast_nd(x, ndim=5, xp=xp)
        assert_array_equal(y, 3 * xp.ones((1, 1, 1, 1, 1)))

    def test_5D(self):
        x = xp.ones((1, 1, 1, 1, 1))

        y = atleast_nd(x, ndim=0, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=4, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=5, xp=xp)
        assert_array_equal(y, x)

        y = atleast_nd(x, ndim=6, xp=xp)
        assert_array_equal(y, xp.ones((1, 1, 1, 1, 1, 1)))

        y = atleast_nd(x, ndim=9, xp=xp)
        assert_array_equal(y, xp.ones((1, 1, 1, 1, 1, 1, 1, 1, 1)))


class TestKron:
    def test_basic(self):
        # Using 0-dimensional array
        a = xp.asarray(1)
        b = xp.asarray([[1, 2], [3, 4]])
        k = xp.asarray([[1, 2], [3, 4]])
        assert_array_equal(kron(a, b, xp=xp), k)
        a = xp.asarray([[1, 2], [3, 4]])
        b = xp.asarray(1)
        assert_array_equal(kron(a, b, xp=xp), k)

        # Using 1-dimensional array
        a = xp.asarray([3])
        b = xp.asarray([[1, 2], [3, 4]])
        k = xp.asarray([[3, 6], [9, 12]])
        assert_array_equal(kron(a, b, xp=xp), k)
        a = xp.asarray([[1, 2], [3, 4]])
        b = xp.asarray([3])
        assert_array_equal(kron(a, b, xp=xp), k)

        # Using 3-dimensional array
        a = xp.asarray([[[1]], [[2]]])
        b = xp.asarray([[1, 2], [3, 4]])
        k = xp.asarray([[[1, 2], [3, 4]], [[2, 4], [6, 8]]])
        assert_array_equal(kron(a, b, xp=xp), k)
        a = xp.asarray([[1, 2], [3, 4]])
        b = xp.asarray([[[1]], [[2]]])
        k = xp.asarray([[[1, 2], [3, 4]], [[2, 4], [6, 8]]])
        assert_array_equal(kron(a, b, xp=xp), k)

    def test_kron_smoke(self):
        a = xp.ones([3, 3])
        b = xp.ones([3, 3])
        k = xp.ones([9, 9])

        assert_array_equal(kron(a, b, xp=xp), k)

    @pytest.mark.parametrize(
        ("shape_a", "shape_b"),
        [
            ((1, 1), (1, 1)),
            ((1, 2, 3), (4, 5, 6)),
            ((2, 2), (2, 2, 2)),
            ((1, 0), (1, 1)),
            ((2, 0, 2), (2, 2)),
            ((2, 0, 0, 2), (2, 0, 2)),
        ],
    )
    def test_kron_shape(self, shape_a, shape_b):
        a = xp.ones(shape_a)
        b = xp.ones(shape_b)
        normalised_shape_a = xp.asarray(
            (1,) * max(0, len(shape_b) - len(shape_a)) + shape_a
        )
        normalised_shape_b = xp.asarray(
            (1,) * max(0, len(shape_a) - len(shape_b)) + shape_b
        )
        expected_shape = tuple(
            int(dim) for dim in xp.multiply(normalised_shape_a, normalised_shape_b)
        )

        k = kron(a, b, xp=xp)
        assert_equal(k.shape, expected_shape, err_msg="Unexpected shape from kron")


class TestExpandDims:
    def test_functionality(self):
        def _squeeze_all(b: Array) -> Array:
            """Mimics `np.squeeze(b)`. `xpx.squeeze`?"""
            for axis in range(b.ndim):
                with contextlib.suppress(ValueError):
                    b = xp.squeeze(b, axis=axis)
            return b

        s = (2, 3, 4, 5)
        a = xp.empty(s)
        for axis in range(-5, 4):
            b = expand_dims(a, axis=axis, xp=xp)
            assert b.shape[axis] == 1
            assert _squeeze_all(b).shape == s

    def test_axis_tuple(self):
        a = xp.empty((3, 3, 3))
        assert expand_dims(a, axis=(0, 1, 2), xp=xp).shape == (1, 1, 1, 3, 3, 3)
        assert expand_dims(a, axis=(0, -1, -2), xp=xp).shape == (1, 3, 3, 3, 1, 1)
        assert expand_dims(a, axis=(0, 3, 5), xp=xp).shape == (1, 3, 3, 1, 3, 1)
        assert expand_dims(a, axis=(0, -3, -5), xp=xp).shape == (1, 1, 3, 1, 3, 3)

    def test_axis_out_of_range(self):
        s = (2, 3, 4, 5)
        a = xp.empty(s)
        with pytest.raises(IndexError, match="out of bounds"):
            expand_dims(a, axis=-6, xp=xp)
        with pytest.raises(IndexError, match="out of bounds"):
            expand_dims(a, axis=5, xp=xp)

        a = xp.empty((3, 3, 3))
        with pytest.raises(IndexError, match="out of bounds"):
            expand_dims(a, axis=(0, -6), xp=xp)
        with pytest.raises(IndexError, match="out of bounds"):
            expand_dims(a, axis=(0, 5), xp=xp)

    def test_repeated_axis(self):
        a = xp.empty((3, 3, 3))
        with pytest.raises(ValueError, match="Duplicate dimensions"):
            expand_dims(a, axis=(1, 1), xp=xp)

    def test_positive_negative_repeated(self):
        # https://github.com/data-apis/array-api/issues/760#issuecomment-1989449817
        a = xp.empty((2, 3, 4, 5))
        with pytest.raises(ValueError, match="Duplicate dimensions"):
            expand_dims(a, axis=(3, -3), xp=xp)
