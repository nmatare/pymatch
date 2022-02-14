#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ London Stock Exchange """

from typing import Dict
import dataclasses

from pymatch._typing import Order
from pymatch import order as order_lib, errors


def _setsmm_string_to_side(x: str) -> type:
    if x == 'A':
        return order_lib.OrderSide.ASK
    elif x == 'B':
        return order_lib.OrderSide.BID
    else:
        raise errors.InvalidOrderFormatError(
            'Expected on of `{}`. Received `{}`'.format(['A', 'B'], x)
        )


MESSAGE_FORMAT_INDEX_TO_PARAMS = {
    0: 'side',
    1: 'identity',
    2: 'price',
    3: 'quantity',
    4: 'peak_size',
}


MESSAGE_FORMAT_SETSmm = {
    # Message format as given by the `SETSmm and Iceberg Orders`
    # technical specification
    #
    # A tuple of size two containing the type and any validation
    #
    0: _setsmm_string_to_side,  # char orderside
    1: int,  # id bigint
    2: int,  # price int
    3: int,  # quantity bigint
    4: int,  # peak size bigint
}


def build_order_from_ascii_string(string: str) -> Order:
    r""" Creates an order based on the "SETSmm specification.

    Parameters:
        string: an ascii encoded string representing the message

    Returns:
        Either a `LimitOrder` or `IcebergOrder`
    """

    fields = _validate_order_string(string)

    if MESSAGE_FORMAT_INDEX_TO_PARAMS[4] in fields:
        return LSEIcebergOrder(**fields, _private_call=False)
    else:
        return LSELimitOrder(**fields, _private_call=False)


@dataclasses.dataclass(init=False, repr=False)
class LSELimitOrder(order_lib.LimitOrder):
    @classmethod
    def from_ascii_string(cls, string: str) -> Order:
        fields = _validate_order_string(string)
        return cls(**fields, _private_call=False)


@dataclasses.dataclass(init=False, repr=False)
class LSEIcebergOrder(order_lib.IcebergOrder):
    @classmethod
    def from_ascii_string(cls, string: str) -> Order:
        fields = _validate_order_string(string)
        return cls(**fields, _private_call=False)


def _validate_order_string(
    x: str, delimiter: str = ',', should_validate: bool = True,
) -> Dict:

    if not isinstance(x, str):
        raise TypeError('Invalid type `%s` ' % type(x))

    if delimiter not in x:
        raise ValueError('Could not find the "%s" delimiter. ' % delimiter)

    fields = {}
    for index, field in enumerate(x.split(delimiter)):

        try:
            validator = MESSAGE_FORMAT_SETSmm[index]

            if validator is not None:
                validated_field = validator(field)
            else:
                validated_field = field

        except KeyError:
            raise errors.InvalidOrderFieldError(
                'Received an invalid order field(%s). ' % index
            )

        fields[MESSAGE_FORMAT_INDEX_TO_PARAMS[index]] = validated_field

    return fields


# EOF
