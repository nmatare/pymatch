#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ LSE Orderbook """


from pymatch import orderbook as orderbook_lib, order as order_lib
from pymatch._typing import Order


class LSEOrderbook(orderbook_lib._BaseOrderbook):
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
                    # order becomes unfilled and the remainder sits on the book
                    making_orderbook.add(order)
                break

            queue_position = 0
            while queue_position < len(queue):  # [2] O(log(n))

                resting_order = queue[queue_position]
                matched_price = resting_order.price

                if resting_order.quantity >= order.quantity:
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

                    if resting_order.quantity == 0:
                        del queue[queue_position]  # [2]

                else:
                    # Case 1: resting order does not have enough volume to
                    # fill order. Use the entire order and move to the next
                    matched_quantity = resting_order.quantity

                    order.quantity = order.quantity - resting_order.quantity
                    resting_order.quantity = 0

                    # => Remove and continue to next resting order or next
                    # price level
                    del queue[queue_position]  # [2]

                    should_break = False
                    queue_position += 1

                if self._is_display:

                    # Update the display quantity of the order given the match
                    resting_order._update_display_quantity(matched_quantity)

                    self._output_trade_message(
                        order, resting_order, matched_price, matched_quantity,
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


# EOF
