#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ LSE Orderbook """

from pymatch import orderbook as orderbook_lib, order as order_lib, errors
from pymatch._typing import Order


class LSEOrderbook(orderbook_lib._BaseOrderbook):
    r""" The `PriceTimePriorityOrderbook` orderbook adds and fills orders
    to the orderbook in price-time priority.
    """

    def cancel(self, order: Order) -> None:
        raise errors.OrderbookMethodNotSupportedError(
            'Canceling orders is not yet supported! '
        )

    def modify(self, order: Order) -> None:
        raise errors.OrderbookMethodNotSupportedError(
            'Modifying orders it not yet supported! '
        )

    def add(self, order: Order) -> None:  # noqa: C901

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
                # [1] O(log(n))
                price, queue = taking_orderbook.peekitem(index)
            except IndexError:
                if order.quantity > 0:
                    # Case 1:
                    # The price-level does not yet exist so this becomes
                    # a passive order that sits on the book
                    #
                    # Case 2:
                    # The order has eaten through all price-levels of the book
                    # There is not enough liquidity and the aggressive order
                    # becomes unfilled, sitting on the top of the book
                    making_orderbook.add(order)
                break

            if order.type is not order_lib.OrderType.MARKET:
                # Only market orders can eat through all available levels.
                # All other orders are limits, and can only execute at
                # better prices:
                if index == 0 and order.price - price >= 0:  # buy-order
                    pass
                elif index < 0 and price - order.price >= 0:  # sell-order
                    pass
                else:
                    making_orderbook.add(order)  # [3]
                    break

            queue_position = 0
            peaked_matches = {}
            while queue_position < len(queue):  # [2] O(log(n))

                resting_order = queue[queue_position]
                matched_price = resting_order.price

                if resting_order.display_quantity >= order.quantity:
                    # Case 0: resting order (or ice berg peak)
                    # has enough volume to totally fill order + reserve

                    matched_quantity = order.quantity
                    resting_order.quantity -= matched_quantity
                    order.quantity = 0

                    should_break = True

                    if resting_order.quantity == 0:
                        del queue[queue_position]  # [2]

                elif resting_order.type is order_lib.OrderType.ICEBERG:

                    should_break = True

                    if len(queue) == 1:
                        # Case 1A: If we only have this iceberg order
                        # then we can use all of its available quantity
                        # otherwise we must cycle through all limits orders
                        # and ice-berg peaks

                        matched_quantity = min(
                            order.quantity, resting_order.quantity
                        )

                        resting_order.quantity -= matched_quantity
                        order.quantity -= matched_quantity

                        if resting_order.quantity == 0:
                            del queue[queue_position]  # [2]

                    else:
                        # Case 1B: special handing of iceberg orders
                        # i) order is greater than the peak
                        # ii) ice-berg peaks must maintain time-priority among
                        # each other
                        del queue_position
                        del resting_order

                        queue_position = 0
                        while queue_position < len(queue):  # [2]
                            # Recursively re-enter the queue and build up
                            # peak executions
                            resting_order = queue[queue_position]

                            matched_quantity = min(
                                order.quantity, resting_order.display_quantity
                            )

                            order.quantity -= matched_quantity
                            resting_order.quantity -= matched_quantity

                            resting_order._update_display_quantity(
                                matched_quantity
                            )

                            if (
                                resting_order.identity not in peaked_matches
                            ):  # noqa: E501
                                new_execution = [
                                    matched_quantity,
                                    resting_order,
                                ]  # noqa: E501
                                peaked_matches[
                                    resting_order.identity
                                ] = new_execution  # noqa: E501
                            else:
                                last_execution = peaked_matches[
                                    resting_order.identity
                                ]  # noqa: E501
                                last_execution[0] += matched_quantity

                            if resting_order.quantity == 0:
                                del queue[queue_position]  # [2]

                            # Exit only if we fill the order or we have
                            # consumed all the orders in the queue
                            if order.quantity <= 0:
                                break

                            queue_position += 1
                            if len(queue) <= queue_position:
                                queue_position = 0  # new cycle

                        if self._is_display:
                            # Print as an aggregated match
                            for (
                                matched_quantity,
                                resting_order,
                            ) in peaked_matches.values():
                                self._output_trade_message(
                                    order,
                                    resting_order,
                                    matched_price,
                                    matched_quantity,
                                )

                else:
                    # Case 2: resting order does not have enough volume to
                    # fill order. Use the entire order and move to the next
                    matched_quantity = resting_order.quantity
                    order.quantity -= resting_order.quantity
                    resting_order.quantity = 0

                    # => Remove and continue to next resting order or next
                    # price level
                    del queue[queue_position]  # [2]

                    should_break = False
                    queue_position += 1

                if not peaked_matches:
                    # If the dict is not populated then we never iterated
                    # through multiple peaks.

                    # Update the display quantity of the order given the match
                    resting_order._update_display_quantity(matched_quantity)

                    if self._is_display:
                        self._output_trade_message(
                            order,
                            resting_order,
                            matched_price,
                            matched_quantity,
                        )

                if should_break:
                    break

            if not queue:
                # queue is depleted remove the price-level
                del taking_orderbook[price]  # [1] - approximate

            if order.quantity > 0:
                # Move onto the next available price level:
                # We may have deleted the best available price, so the next
                # `index` will become the next best
                pass
            else:
                break  # break top-level while loop

        if self._is_display:
            return self._output_quote_message()


# EOF
