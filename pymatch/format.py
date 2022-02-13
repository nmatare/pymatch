#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Formatting for orderbook output """

import abc
import sys

import itertools
import threading
import queue

from pymatch._typing import Order


_BOOK_FORMAT_HEADER = """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
"""

BOOK_FORMAT_BODY_BID = '|{:>10}|{:>13,}|{:>7,}'
BOOK_FORMAT_BODY_ASK = '|{:>7,}|{:>13,}|{:>10}|'

_BOOK_FORMAT_FOOTER = (
    '\n+-----------------------------------------------------------------+'
)

_BOOK_FORMAT_BODY = """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|          |             |       |       |             |          |
+-----------------------------------------------------------------+
"""


class DISPLAY_BOOK_FORMAT:
    r""" A global class definition used by the calling program to update
    the displayed state of the orderbook.

    This allows us to update both the actual and displayed state of
    the orderbook at the same time. Writing of the updated state is conferred
    to a seperate thread for performance reasons.
    """

    @classmethod
    def modify_price(cls, price: int, volume: float):
        breakpoint()

    @classmethod
    def modify_volume(cls, price: int, position: int, volume: float):
        breakpoint()


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
        from pymatch import order as order_lib  # potential circular

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


class _CaptureOutputThreadWorker:
    def __init__(
        self, should_capture_output: bool, *args, **kwargs,
    ):
        self._should_capture_output = should_capture_output

    def capture_trade(self, *args) -> None:
        message_string = TradeFormat.from_orders(*args)

        if self._should_capture_output:
            sys.stdout.write(message_string.body)

    def capture_quote(self, *args) -> None:
        breakpoint()

    def send(self, *args, format_: _Format) -> None:
        message_string = format_(*args)
        sys.stdout.write(message_string.body)
        self._task_queue.task_done()

        format_ = (format_lib.TradeFormat.from_orders,)


# class _CaptureOutputThreadWorker(threading.Thread):

# def __init__(
# self,
# should_capture_output: bool,
# *args,
# **kwargs,
# ):
# self._should_capture_output = should_capture_output
# self._task_queue = queue.Queue()
# super().__init__(*args, daemon=True, **kwargs)

# def send(self, *args, format_: _Format) -> None:
# self._task_queue.put(format_(*args))

# def run(self):

# while self._should_capture_output:
# message_string = self._task_queue.get()

# sys.stdout.write(message_string.body)

# self._task_queue.task_done()

# EOF
