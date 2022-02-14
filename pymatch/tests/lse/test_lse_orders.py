#!/usr/bin/python
# -*- coding: utf-8 -*-
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Test Orders """

import pytest

from pymatch import errors
from pymatch import lse as lse_order_lib, order as order_lib


class TestLimitOrders:
    def test_build_valid_limit_order(self) -> None:

        x = 'B,100322,5103,7500'
        order = lse_order_lib.build_order_from_ascii_string(x)

        assert order.price == 5103
        assert order.quantity == 7500
        assert order.display_quantity == 7500
        assert order.side == order_lib.OrderSide.BUY
        assert order.type == order_lib.OrderType.LIMIT
        assert order.identity == 100322

    def test_build_invalid_limit_order(self) -> None:

        x = 'S,100322,5103,7500'

        with pytest.raises(errors.InvalidOrderFormatError):
            lse_order_lib.build_order_from_ascii_string(x)

    def test_build_valid_iceberg_order(self) -> None:

        x = 'A,100345,5103,100000,10000'
        order = lse_order_lib.build_order_from_ascii_string(x)

        assert order.price == 5103
        assert order.quantity == 100_000
        assert order.display_quantity == 10_000
        assert order.side == order_lib.OrderSide.SELL
        assert order.type == order_lib.OrderType.ICEBERG
        assert order.identity == 100345

    def test_build_invalid_iceberg_order(self) -> None:

        x = 'S,100345,5103,100000,0'

        with pytest.raises(errors.InvalidOrderFormatError):
            lse_order_lib.build_order_from_ascii_string(x)


# EOF
