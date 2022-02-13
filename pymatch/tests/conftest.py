#!/usr/bin/python
# -*- coding: utf-8 -*-
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Testing configuration """

import numpy as np
import sys

from pymatch import order as order_lib


def generate_testing_orders(
    ask_sigma: float = 1.0,
    bid_sigma: float = 1.0,
    num_orders_per_side: int = 100_000_000,
    seed: int = 666,
) -> list:

    np.random.seed(seed)

    def build_orders(sigma: float, side: str):
        def _build_distribution(sigma) -> np.ndarray:
            return (
                np.random.lognormal(0, sigma, num_orders_per_side) * 1000
            ).astype(np.int32)

        sizes = np.random.uniform(1, 100, num_orders_per_side).astype(np.int32)

        orders = []
        for index, (price, size) in enumerate(
            zip(_build_distribution(sigma), sizes),
        ):
            orders.append(f'{side},{index},{price},{size}')

        return orders

    orders = []
    orders.extend(build_orders(ask_sigma, 'A'))
    orders.extend(build_orders(bid_sigma, 'B'))
    np.random.shuffle(orders)
    return orders


def run_orderbook(orderbook: type, orders: list) -> None:

    made_orders = []
    for line in orders:
        made_orders.append(order_lib.build_order_from_ascii_string(line))

    for order in made_orders:
        orderbook.add(order)

        if (
            orderbook.best_ask is not sys.maxsize
            and orderbook.best_bid is not sys.maxsize
        ):
            assert orderbook.best_ask - orderbook.best_bid


# EOF
