#!/usr/bin/python
# -*- coding: utf-8 -*-
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Test Orderbook """

import os
import io
import sys
import copy
import contextlib

from pymatch import lse as lse_order_lib
from pymatch.tests.lse import conftest


_TEST_ADD_LIMIT_ORDER_STDOUT_EXPECTED_OUTPUT = """
+-----------------------------------------------------------------+
| BUY                            | SELL                           |
| Id       | Volume      | Price | Price | Volume      | Id       |
+----------+-------------+-------+-------+-------------+----------+
|1234567890|1,234,567,890| 32,503| 32,504|1,234,567,890|1234567891|
|      1138|        7,500| 31,502| 32,505|        7,777|      6808|
|          |             |       | 32,507|        3,000|     42100|
+-----------------------------------------------------------------+
"""


class TestLimitOrder:
    def test_add_limit_order(self):

        orderbook = lse_order_lib.LSEOrderbook()

        with open(os.devnull, 'w') as null:
            with contextlib.redirect_stdout(null):
                x = 'B,1234567890,32503,1234567890'
                buy_order_1 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(buy_order_1)

                x = 'A,1234567891,32504,1234567890'
                sell_order_1 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_1)

                x = 'A,6808,32505,7777'
                sell_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_2)

                x = 'B,1138,31502,7500'
                buy_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(buy_order_2)

                x = 'A,42100,32507,3000'
                sell_order_3 = lse_order_lib.build_order_from_ascii_string(x)

        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(sell_order_3)

            stdout = stream.getvalue()

        assert stdout == _TEST_ADD_LIMIT_ORDER_STDOUT_EXPECTED_OUTPUT.rstrip()
        assert orderbook.best_bid == 32503
        assert orderbook.best_ask == 32504

    def test_single_match_with_fully_aggressive_limit_order(self):

        # One for one match to resting order
        orderbook = lse_order_lib.LSEOrderbook()

        with open(os.devnull, 'w') as null:
            with contextlib.redirect_stdout(null):
                x = 'B,100322,5103,7500'
                resting_order = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(resting_order)

        x = 'A,100345,5103,7499'
        aggressive_order = lse_order_lib.build_order_from_ascii_string(x)

        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order)
                stdout = stream.getvalue()

        assert stdout.split('\n')[1] == '100322,100345,5103,7499'

    def test_multiple_match_fully_aggressive_limit_order(self):
        # Eats through multiple orders multiple levels until remaining
        # is left on the book
        orderbook = lse_order_lib.LSEOrderbook()

        with open(os.devnull, 'w') as null:
            with contextlib.redirect_stdout(null):
                x = 'A,10,32504,444'
                sell_order_1 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_1)

                x = 'A,11,32505,555'
                sell_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_2)

                x = 'A,12,32507,777'
                sell_order_3 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_3)

                x = 'B,99,33000,445'
                aggressive_order_1 = lse_order_lib.build_order_from_ascii_string(
                    x
                )
                orderbook.add(aggressive_order_1)

        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order_1)
            stdout = stream.getvalue()

        assert orderbook.best_ask == 32505
        assert orderbook.best_bid == sys.maxsize  # aka NaN
        assert orderbook.asks[32505][0].quantity == 554  # took one
        assert '32,504' not in stdout
        assert '32,505' in stdout

        # Submit a much larger aggressive and observe
        # that the remainder is now on the book:
        x = 'B,100,33000,10000'
        aggressive_order_2 = lse_order_lib.build_order_from_ascii_string(x)

        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order_2)
            stdout = stream.getvalue()

        assert orderbook.best_bid == 33000
        assert orderbook.best_ask == sys.maxsize  # aka NaN
        assert orderbook.bids[33000][0].quantity == 10_000 - 554 - 777

        assert '32,504' not in stdout
        assert '32,505' not in stdout
        assert '32,507' not in stdout
        assert '33,000' in stdout


class TestIcebergOrder:

    # These testcases adopted from:
    # ref: SETSmm and Iceberg Orders SERVICE & TECHNICAL DESCRIPTION
    # 4.2.3 How iceberg orders work

    def test_add_aggressive_iceberg_order(self):

        orderbook = lse_order_lib.LSEOrderbook()

        with open(os.devnull, 'w') as null:
            with contextlib.redirect_stdout(null):
                x = 'B,1,99,50000'
                buy_order_1 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(buy_order_1)

                x = 'B,2,98,25500'
                buy_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(buy_order_2)

                x = 'A,3,100,10000'
                sell_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_2)

                x = 'A,4,100,7500'
                sell_order_3 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_3)

                x = 'A,5,101,20000'
                sell_order_4 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_4)

        x = 'B,99,100,100000,10000'
        aggressive_order_1 = lse_order_lib.build_order_from_ascii_string(x)

        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order_1)

        assert orderbook.best_ask == 101
        assert orderbook.best_bid == 100
        assert orderbook.bids[100][0].quantity == 82500
        assert orderbook.bids[100][0].peak_quantity == 10000

    def test_add_passive_iceberg_order(self):
        orderbook = lse_order_lib.LSEOrderbook()

        with open(os.devnull, 'w') as null:
            with contextlib.redirect_stdout(null):
                x = 'B,1,99,50000'
                buy_order_1 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(buy_order_1)

                x = 'B,2,98,25500'
                buy_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(buy_order_2)

                x = 'A,3,100,10000'
                sell_order_2 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_2)

                x = 'A,4,100,7500'
                sell_order_3 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_3)

                x = 'A,5,101,20000'
                sell_order_4 = lse_order_lib.build_order_from_ascii_string(x)
                orderbook.add(sell_order_4)

                x = 'B,88,100,100000,10000'
                iceberg_order_1 = lse_order_lib.build_order_from_ascii_string(
                    x
                )
                orderbook.add(iceberg_order_1)

                x = 'A,999,100,10000'
                aggressive_order_1 = lse_order_lib.build_order_from_ascii_string(
                    x
                )

        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order_1)

            stdout = stream.getvalue()

        assert stdout.split('\n')[1] == '88,999,100,10000' in stdout
        assert orderbook.best_ask == 101
        assert orderbook.best_bid == 100
        assert orderbook.bids[100][0].quantity == 72500
        assert orderbook.bids[100][0].peak_quantity == 10000

        x = 'A,9999,100,11000'
        aggressive_order_2 = lse_order_lib.build_order_from_ascii_string(x)

        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order_2)
            stdout = stream.getvalue()

        # "Multiple executions of an iceberg order on the order book will
        # only generate a single
        # trade message (5TG) for the iceberg participant
        # (ie when an incoming order executes
        # against the peak of an iceberg order and some or all
        # of the hidden volume)."

        assert stdout.split('\n')[1] == '88,9999,100,11000' in stdout
        assert orderbook.best_ask == 101
        assert orderbook.best_bid == 100
        assert orderbook.bids[100][0].quantity == 61500
        assert orderbook.bids[100][0].peak_quantity == 9000

        # Now add second iceberg order
        x = 'B,888,100,50000,20000'
        iceberg_order_2 = lse_order_lib.build_order_from_ascii_string(x)
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(iceberg_order_2)
        assert len(orderbook.bids[100]) == 2  # now 2 iceberg orders

        x = 'A,99999,100,35000'
        aggressive_order_3 = lse_order_lib.build_order_from_ascii_string(x)
        # check final stdout
        with io.StringIO() as stream:
            with contextlib.redirect_stdout(stream):
                orderbook.add(aggressive_order_3)
            stdout = stream.getvalue()

        # "For example, if an order to
        # sell 35,000 shares At Best is now entered at 8:30,
        # then the visible peaks of both
        # icebergs will be completely filled, and iceberg A will
        # satisfy the remaining 6,000
        # shares of the incoming order."

        assert orderbook.bids[100][0].quantity == (61500 - 15000)
        assert orderbook.bids[100][0].peak_quantity == 4000

        assert orderbook.bids[100][1].quantity == (50000 - 20000)
        assert orderbook.bids[100][1].peak_quantity == 20000

        # We should see two trade messages
        assert stdout.split('\n')[1] == '88,99999,100,15000' in stdout
        assert stdout.split('\n')[2] == '888,99999,100,20000' in stdout


def test_profile_orderbook(iterations: int = 1):

    # read from dumped testing data file
    # profile this bad boy:
    lines = conftest.generate_testing_orders(num_orders_per_side=10_000,)

    fixed = []
    for line in lines:
        order = lse_order_lib.build_order_from_ascii_string(line)
        fixed.append(order)

    orders = []
    for _ in range(iterations):
        orders.append(copy.deepcopy(fixed))

    from pyinstrument import Profiler

    profiler = Profiler()
    profiler.start()
    print('\n--- Profling testcase ---')

    for i in range(iterations):
        orderbook = lse_order_lib.LSEOrderbook(is_display=False)
        conftest.run_orderbook(orderbook, orders[i])

    profiler.stop()

    print(
        profiler.output_text(
            unicode=True, color=True, show_all=True, timeline=False
        )
    )


# EOF
