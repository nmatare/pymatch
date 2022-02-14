#!/usr/bin/python
# -*- coding: utf-8 -*-
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Helper modules """

import sys

from pymatch import lse as lse_order_lib, orderbook as orderbook_lib

PROGRAM_HEADER = """
██████╗ ██╗   ██╗███╗   ███╗ █████╗ ████████╗ ██████╗██╗  ██╗
██╔══██╗╚██╗ ██╔╝████╗ ████║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
██████╔╝ ╚████╔╝ ██╔████╔██║███████║   ██║   ██║     ███████║
██╔═══╝   ╚██╔╝  ██║╚██╔╝██║██╔══██║   ██║   ██║     ██╔══██║
██║        ██║   ██║ ╚═╝ ██║██║  ██║   ██║   ╚██████╗██║  ██║
╚═╝        ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
"""


def _run_lse_orderbook_from_stdin():

    sys.stdout.write('[INFO] - Expecting input from stdin...\n')

    orderbook = lse_order_lib.LSEOrderbook()

    orders = []
    if not sys.stdin.isatty():
        for line in sys.stdin:
            order = lse_order_lib.build_order_from_ascii_string(line)
            # make the orders first, for performance
            orders.append(order)

    for order in orders:
        orderbook.add(order)

    for line in sys.stdin:

        order = lse_order_lib.build_order_from_ascii_string(line)

        orderbook.add(order)


if __name__ == '__main__':

    import os

    sys.stdout.write(f'{PROGRAM_HEADER}\n')

    if not os.getenv(orderbook_lib.ENV_VAR_ENABLE_PROFILING):

        sys.stdout.write(
            '[WARNING] - Printing orderbook output to stdout. '
            'This will severly degrade performance! '
            'Set the `ENABLE_PROFILING=1` flag to enable profiling...\n'
        )

    _run_lse_orderbook_from_stdin()

    sys.stdout.write('\n[INFO] - Finished!\n')

# EOF
