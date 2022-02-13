#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Messages """


MESSAGE_FORMAT_INDEX_TO_PARAMS = {
    0: 'side',
    1: 'identity',
    2: 'price',
    3: 'quantity',
    4: 'peak_size',
}


def _validate_message_format_setsmm_side(x: str) -> type:

    from pymatch.order import OrderSide  # potential circular

    return OrderSide.from_SETSmm_ascii_string(x)


MESSAGE_FORMAT_SETSmm = {
    # Message format as given by the `SETSmm and Iceberg Orders`
    # technical specification
    #
    # A tuple of size two containing the type and any validation
    #
    0: _validate_message_format_setsmm_side,  # char orderside
    1: int,  # id bigint
    2: int,  # price int
    3: int,  # quantity bigint
    4: int,  # peak size bigint
}

# EOF
