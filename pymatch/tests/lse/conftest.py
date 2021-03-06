#!/usr/bin/python
# -*- coding: utf-8 -*-
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ pytest configuration file for the LSE exchange """

from typing import List
import sys

import numpy as np


def generate_testing_orders(
    ask_sigma: float = 1.0,
    bid_sigma: float = 1.0,
    num_orders_per_side: int = 10_000_000,
    seed: int = 666,
) -> List:

    np.random.seed(seed)

    def build_orders(sigma: float, side: str, is_iceberg: bool = False):
        def _build_distribution(sigma) -> np.ndarray:
            return (
                np.random.lognormal(0, sigma, num_orders_per_side) * 1000
            ).astype(np.int32)

        sizes = np.random.uniform(1, 100, num_orders_per_side).astype(np.int32)

        orders = []
        for index, (price, size) in enumerate(
            zip(_build_distribution(sigma), sizes),
        ):
            line = f'{side},{index},{price},{size}'

            if is_iceberg and size > 1:
                peak_size = np.random.randint(1, size + 1)
                if peak_size == size:
                    continue
                line += f',{peak_size}'

            orders.append(line)

        return orders

    orders = []
    orders.extend(build_orders(ask_sigma, 'A'))
    orders.extend(build_orders(bid_sigma, 'B'))
    orders.extend(build_orders(ask_sigma, 'A', True))
    orders.extend(build_orders(bid_sigma, 'B', True))
    np.random.shuffle(orders)
    return orders


def run_orderbook(
    orderbook: type, orders: List, validate: bool = False,
) -> None:

    for order in orders:
        orderbook.add(order)

        if validate:
            if (
                orderbook.best_ask is not sys.maxsize
                and orderbook.best_bid is not sys.maxsize
            ):
                assert orderbook.best_ask - orderbook.best_bid


# EOF
