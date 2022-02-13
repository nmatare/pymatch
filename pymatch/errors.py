#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Orderbook """


class OrderError(Exception):
    pass


class InvalidOrderFormatError(OrderError):
    pass


class InvalidOrderFieldError(OrderError):
    pass


class OrderbookError(Exception):
    pass


class OrderbookMethodNotSupportedError(OrderbookError):
    pass


class TickTapeIsNotMonotonicError(OrderbookError):
    pass


# EOF
