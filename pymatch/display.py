#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Formatting for orderbook output """

import abc
import itertools

from pymatch._typing import Order
from pymatch import order as order_lib


BOOK_FORMAT_BODY_BID = '|{:>10}|{:>13,}|{:>7,}'
BOOK_FORMAT_BODY_ASK = '|{:>7,}|{:>13,}|{:>10}|'

_BOOK_FORMAT_HEADER = """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
"""

_BOOK_FORMAT_FOOTER = (
    '\n+-----------------------------------------------------------------+'
)


class _Format(abc.ABC):

    _message: str = ''

    @property
    def body(self) -> str:
        return self.header + self._message + self.footer

    @abc.abstractproperty
    def header(self) -> str:
        pass

    @abc.abstractproperty
    def footer(self) -> str:
        pass


class BookFormat(_Format):
    def __init__(self, bids: type, asks: type):
        def make_empty(format_: str) -> str:
            return format_.format(0, 0, 0).replace('0', ' ')  # noqa: E231

        messages = []
        for bid_message, ask_message in itertools.zip_longest(
            bids.to_display(), asks.to_display(),
        ):
            if bid_message is None:
                bid_message = make_empty(BOOK_FORMAT_BODY_BID)

            if ask_message is None:
                ask_message = make_empty(BOOK_FORMAT_BODY_ASK)

            messages.append(bid_message + ask_message)

        if not messages:
            messages.append(
                make_empty(BOOK_FORMAT_BODY_BID)
                + make_empty(BOOK_FORMAT_BODY_ASK)
            )

        self._message = '\n'.join(messages)

    @property
    def header(self) -> str:
        return _BOOK_FORMAT_HEADER

    @property
    def footer(self) -> str:
        return _BOOK_FORMAT_FOOTER


class TradeFormat(_Format):
    def __init__(
        self,
        buy_order_id: int,
        sell_order_id: int,
        price: int,
        quantity: int,
        delimiter: str = ',',
    ):
        self._message = f'{delimiter}'.join(
            [str(buy_order_id), str(sell_order_id), str(price), str(quantity),]
        )

        super().__init__()

    @classmethod
    def from_orders(
        cls,
        aggressive_order: Order,
        resting_order: Order,
        matched_price: int,
        matched_quantity: int,
    ):

        if aggressive_order.side is order_lib.OrderSide.BID:
            buy_order_id = aggressive_order.identity
            sell_order_id = resting_order.identity
        else:
            buy_order_id = resting_order.identity
            sell_order_id = aggressive_order.identity

        return cls(
            buy_order_id, sell_order_id, matched_price, matched_quantity,
        )

    @property
    def header(self) -> str:
        return '\n'

    @property
    def footer(self) -> str:
        return ''


# EOF
