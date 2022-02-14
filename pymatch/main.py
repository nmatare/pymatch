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


def run_lse_orderbook_from_stdin():

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
        profiler = None

        sys.stdout.write(
            '[WARNING] - Printing orderbook output to stdout. '
            'This will severly degrade performance! '
            'Set the `ENABLE_PROFILING=1` to enable profiling...\n'
        )

    else:

        try:
            from pyinstrument import Profiler

            profiler = Profiler()
            profiler.start()

        except ImportError as exc_info:
            raise ImportError(
                'Could not find the `pyinstrument` package. '
                'Did you install the program with `pip install .[tests]` ?'
            ) from exc_info

    run_lse_orderbook_from_stdin()

    if profiler is not None:

        profiler.stop()

        sys.stdout.write('\n')
        sys.stdout.write(
            profiler.output_text(
                unicode=True, color=True, show_all=True, timeline=False
            )
        )

# EOF
