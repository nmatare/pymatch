#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Orderbook """

from typing import Dict, List

import abc
import os
import sys
import sortedcontainers

from pymatch._typing import Order
from pymatch import errors
from pymatch import order as order_lib, display as display_lib

# Note: all prices and quantities are expressed in integers so to avoid
# using a NaN value like float('Inf') (which is a double), we use the maxsize
# to specify a NaN integer
INTEGER_NAN = sys.maxsize

ENV_VAR_ENABLE_PROFILING = 'ENABLE_PROFILING'


class _PriceLevelContainer(sortedcontainers.SortedDict):
    def __init__(self, side: order_lib.OrderSide):
        self._side = side
        super().__init__()

    def add(self, order: Order) -> List:

        try:
            queue = self[order.price]  # O(log(n))
            queue.append(order)  # O(log(n))
        except KeyError:
            queue = [order]

        self[order.price] = queue  # O(log(n))
        return queue

    def __iter__(self):
        if self._side is order_lib.OrderSide.ASK:
            return super().__iter__()
        return super().__reversed__()

    def to_display(self) -> List:
        lines = []
        for price, queue in self.items():
            for order in queue:
                lines.append(order.to_display())
        return lines


class _BaseOrderbook(abc.ABC):
    r""" The `_BaseOrderbook` class is a base class for implementing all
    ordersbooks in the `pymatch` library. Each superclass should use this
    when constructing orderbooks.
    """

    def __init__(self, is_display: bool = True):
        self._tick_tape = 0

        # Note: Currently, in order to display the orderbook to stdout, the
        # book must be re-iterated which will cause significant slowdowns.
        # Disable displaying to improve performance

        self._is_display = os.getenv(ENV_VAR_ENABLE_PROFILING, is_display)
        self._bids = _PriceLevelContainer(order_lib.OrderSide.BUY)
        self._asks = _PriceLevelContainer(order_lib.OrderSide.ASK)
        # given {price[Integer]: queue[List[Order]]}
        super().__init__()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__qualname__}({round(self.best_bid, 2)}|'
            f'{round(self.best_ask, 2)})'
        )

    @property
    def tick_tape(self) -> int:
        return self._tick_tape

    @tick_tape.setter
    def tick_tape(self, index: int) -> None:
        if 0 < index < self.tick_tape:
            raise errors.TickTapeIsNotMonotonicException(
                f'You attempted to set the tick-tape to a period({index}) '
                f'that occured before the current tick-tape({self._tick_tape})'
                'This is erroneous. Check your inputs. '
            )

        self._tick_tape = index

    @property
    def bids(self) -> Dict:
        return self._bids

    buys = bids  # alias

    @property
    def best_bid(self) -> int:
        return self._best_bid

    @best_bid.getter
    def best_bid(self) -> int:
        try:
            return self.bids.keys()[-1]
        except IndexError:
            return INTEGER_NAN

    @property
    def asks(self) -> Dict:
        return self._asks

    sells = asks  # "

    @property
    def best_ask(self) -> int:
        return self._best_ask

    @best_ask.getter
    def best_ask(self) -> int:
        try:
            return self.asks.keys()[0]
        except IndexError:
            return INTEGER_NAN

    def add(self, order: Order) -> None:
        r""" The `add` method adds an order to the orderbook.

        Parameters:
            order: a `pymatch.order.Order` order

        Returns:
            None
        """

        passive_quote = None

        if order.type is not order_lib.OrderType.MARKET:

            if order.side is order_lib.OrderSide.BID and (
                order.price < self.best_ask or INTEGER_NAN is self.best_ask
            ):
                # Handle buy passive orders
                passive_quote = self._bids.add(order)

            if order.side is order_lib.OrderSide.ASK and (
                order.price > self.best_bid or INTEGER_NAN is self.best_bid
            ):
                # Handle sell passive orders
                passive_quote = self._asks.add(order)

        if not bool(passive_quote) or order.type is order_lib.OrderType.MARKET:
            self._handle_match(order)  # Aggressive matching order

        if self._is_display:
            self._output_quote_message()

    def cancel(self, order: Order) -> None:
        r""" The `cancel` method removes an order from the orderbook.

        Parameters:
            order: a `pymatch.order.Order` order

        Returns:
            None
        """
        raise errors.OrderbookMethodNotSupportedError(
            'Canceling orders is not yet supported! '
        )

    def modify(self, order: Order) -> None:
        r""" The `modify` method modifies an order already on the orderbook.

        Parameters:
            order: a `pymatch.order.Order` order

        Returns:
            None
        """

        raise errors.OrderbookMethodNotSupportedError(
            'Modifying orders it not yet supported! '
        )

    @abc.abstractmethod
    def _handle_match(self, order: Order) -> None:
        r""" Each superclass of `_BaseOrderbook` should implement a
        `_handle_match` which will handle an aggressive match message

        Parameters:
            order: an aggressive order to resolve

        Returns:
            `None`
        """
        pass

    def _output_quote_message(self, *args, **kwargs) -> None:
        message = display_lib.BookFormat(self.bids, self.asks)
        sys.stdout.write(message.body)

    def _output_trade_message(self, *args, **kwargs) -> None:
        message = display_lib.TradeFormat.from_orders(*args, **kwargs)
        sys.stdout.write(message.body)


# EOF
