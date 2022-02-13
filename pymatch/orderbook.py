#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Orderbook """

from typing import Dict, List, Optional

import abc
import sys
import sortedcontainers

from pymatch._typing import Order
from pymatch import errors
from pymatch import order as order_lib, format as format_lib

# Note: all prices and quantities are expressed in integers so to avoid
# using a NaN value like float('Inf') (which is a double), we use the maxsize
# to specify a NaN integer
INTEGER_NAN = sys.maxsize

DISPLAY_BOOK_FORMAT = format_lib.DISPLAY_BOOK_FORMAT  # global class


class _PriceLevelContainer(sortedcontainers.SortedDict):
    def __init__(self, side: order_lib.OrderSide):
        self._side = side
        super().__init__()

    def add(self, order: Order) -> List:
        try:
            queue = self[order.price]  # O(log(n))
            queue.append(order)
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

    def __init__(self, output_stdout: bool = True):
        self._tick_tape = 0
        self._bids = _PriceLevelContainer(order_lib.OrderSide.BUY)
        self._asks = _PriceLevelContainer(order_lib.OrderSide.ASK)
        # given {price[Integer]: queue[List[Order]]}
        self._output_stream = format_lib._CaptureOutputThreadWorker(
            output_stdout
        )
        # self._output_stream.start()
        super().__init__()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__qualname__}({round(self.best_bid, 2)}|'
            f'{round(self.best_ask, 2)})'
        )

    def __del__(self) -> None:
        self._output_stream._should_capture_output = False

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

    def add(self, order: Order) -> None:
        r""" The `add` method adds an order to the orderbook.

        Parameters:
            order: a `pymatch.order.Order` order

        Returns:
            None
        """

        new_price = False

        if order.side is order_lib.OrderSide.BID and (
            order.price < self.best_ask or INTEGER_NAN is self.best_ask
        ):
            new_price = self._bids.add(order)  # Handle buy passive orders

        if order.side is order_lib.OrderSide.ASK and (
            order.price > self.best_bid or INTEGER_NAN is self.best_bid
        ):
            new_price = self._asks.add(order)  # Handle sell passive orders

        if bool(new_price):
            self._update_displayed_orderbook(
                order.price, volume=order.quantity
            )

        else:
            self._handle_match(order)  # Aggressive matching order

        self._flush_displayed_orderbook()

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

    @abc.abstractmethod
    def _flush_displayed_orderbook(self, *args, **kwargs) -> None:
        # Flushes the final results of the orderbook to stdout. That is,
        # all changes must first be applied.
        pass

    def _flush_displayed_trade(self, *args, **kwargs) -> None:
        self._output_stream.capture_trade(*args, **kwargs)


class PriceTimePriorityOrderbook(_BaseOrderbook):
    r""" The `PriceTimePriorityOrderbook` orderbook adds and fills orders
    to the orderbook in price-time priority.
    """

    def _handle_match(self, order: Order) -> None:  # noqa: C901

        if order.side is order_lib.OrderSide.BUY:  # Aggressive buy order
            taking_orderbook = self._asks
            making_orderbook = self._bids
            index = 0

        elif order.side is order_lib.OrderSide.SELL:  # Aggressive sell order
            taking_orderbook = self._bids
            making_orderbook = self._asks
            index = -1

        while 1:
            # Start with the best available price level and work toward the
            # edges of the book
            try:
                price, queue = taking_orderbook.peekitem(
                    index
                )  # [1] O(log(n))  noqa: E501
            except IndexError:
                if order.quantity > 0:
                    # Special Case:
                    # If the order has eaten through all levels of the book,
                    # then there is not enough liquidity and the aggressive
                    # order becomes unfilled and the remainder sit on the book
                    making_orderbook.add(order)
                break

            queue_position = 0
            while queue_position < len(queue):  # [2] O(log(n))

                resting_order = queue[queue_position]
                matched_price = resting_order.price

                if resting_order.quantity > order.quantity:
                    # Case 0: resting order has enough volume to totally
                    # fill order + reserve

                    matched_quantity = order.quantity
                    resting_order.quantity = (
                        # [2] => modifies mutable list in-place
                        resting_order.quantity
                        - order.quantity
                    )
                    should_break = True
                    order.quantity = 0

                    self._update_displayed_orderbook(
                        price, resting_order.quantity, queue_position,
                    )

                elif resting_order.quantity == order.quantity:
                    # Case 1: resting order matches volume completely
                    matched_quantity = resting_order.quantity

                    order.quantity = 0
                    resting_order.quantity = 0
                    should_break = True
                    del queue[queue_position]  # [2]

                    self._update_displayed_orderbook(
                        price, resting_order.quantity, queue_position,
                    )

                else:
                    # Case 2: resting order does not have enough volume to
                    # fill order. Use the entire order and move to the next
                    matched_quantity = resting_order.quantity

                    order.quantity = order.quantity - resting_order.quantity
                    resting_order.quantity = 0

                    # => Remove and continue to next resting order or next
                    # price level
                    self._update_displayed_orderbook(
                        price, resting_order.quantity, queue_position,
                    )

                    del queue[queue_position]  # [2]

                    should_break = False
                    queue_position += 1

                self._flush_displayed_trade(
                    order, resting_order, matched_price, matched_quantity,
                )

                if should_break:
                    break

            if not queue:
                # queue is depleted remove the price-level
                del taking_orderbook[price]  # [1] - approximate

                self._update_displayed_orderbook(price, volume=0.0)

            if order.quantity > 0:
                # Move onto the next available price level:
                # We may have deleted the best available price, so the next
                # `index` will become the next best
                pass
            else:
                break  # break top-level while loop

        def _update_displayed_orderbook(
            self,
            price: int,
            volume: float,
            queue_position: Optional[List] = None,
        ) -> None:
            # Updates the "displayed" orderbook. The orderbook displayed on
            # stdout.

            if queue_position is None:
                # Case 1): Remove an entire price from the book
                DISPLAY_BOOK_FORMAT.modify_price(price, volume)
            else:
                # Case 2): Drop a queue position from the book
                DISPLAY_BOOK_FORMAT.modify_volume(
                    price, queue_position, volume,
                )


# EOF
