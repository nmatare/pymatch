#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Orders """

import abc
import enum
import dataclasses

from typing import Dict, AnyStr

from pymatch._typing import Order
from pymatch import errors, messages, format as format_lib


class OrderSide(enum.IntEnum):

    BID = BUY = 1
    ASK = SELL = -1

    @classmethod
    def from_SETSmm_ascii_string(cls, x: AnyStr) -> enum.IntEnum:
        if x == 'A':
            return cls.ASK
        elif x == 'B':
            return cls.BID
        else:
            raise errors.InvalidOrderFormatError(
                'Expected on of `{}`. Received `{}`'.format(['A', 'B'], x)
            )

    @property
    def to_display(self) -> str:
        if self is self.BID:
            return format_lib.BOOK_FORMAT_BODY_BID
        elif self is self.ASK:
            return format_lib.BOOK_FORMAT_BODY_ASK


@enum.unique
class OrderType(enum.IntEnum):

    UNKNOWN = -1
    LIMIT = 0
    ICEBERG = 1

    @property
    def to_display(self) -> str:
        return self.name.capitalize()


@dataclasses.dataclass(repr=True, init=False)
class _BaseOrder(abc.ABC):
    r""" Base class for constructing `_BaseOrder` orders. All orders using
    the `pymatch` library should use this class when constructing derivative
    orders.
    """

    def __init__(
        self,
        side: OrderSide,
        identity: int,
        price: int,
        quantity: int,
        _private_call: bool = True,
    ):
        r""" Base constructor for building all order super classes.

        Parameters:
            side: the orderside
            identity: an bigint representing the order id
            price: the price of the order
            quantity: the size of the order

        """

        if _private_call:
            raise ValueError('Private call: use one of the factory methods! ')

        self.identity = identity
        self.side = side
        self.price = price
        self.quantity = quantity
        super().__init__()

    def __repr__(self):
        return (
            f'{self.__class__.__qualname__}('
            f'price={self.price} @ quantity={self.quantity})'
        )

    def replace(self, **params) -> Order:
        for key, value in params.items():
            setattr(self, key, value)
        return self

    @property
    def display_quantity(self) -> int:
        return self.quantity

    @classmethod
    def from_fields(cls, **params) -> Order:
        return cls(**params, _private_call=False)

    def to_display(self) -> str:
        args = [self.identity, self.display_quantity, self.price]

        if self.side is OrderSide.ASK:
            args = args[::-1]

        return self.side.to_display.format(*args)


@dataclasses.dataclass(init=False, repr=False)
class LimitOrder(_BaseOrder):
    r""" Creates a limit order, a passive order that is placed onto the book
    at a specified level.
    """
    pass


@dataclasses.dataclass(init=False)
class IcebergOrder(_BaseOrder):
    r""" Creates an iceberg order, a passive order that is placed onto
    the book wherein only the "peak_size" is displayed.
    """

    def __init__(self, peak_size: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.peak_size = self._validate_peak_size(peak_size)

    @property
    def display_quantity(self) -> int:
        return self.peak_size

    def _validate_peak_size(self, peak_size: int) -> int:
        if peak_size > self.quantity:
            raise errors.OrderError(
                'Received an "Iceberg" order with a peak size greater than '
                'the given size. '
            )
        return peak_size


def _validate_order_string(x: str, delimiter: str = ',') -> Dict:

    if not isinstance(x, str):
        raise TypeError('Invalid type `%s` ' % type(x))

    if delimiter not in x:
        raise ValueError('Could not find the "%s" delimiter. ' % delimiter)

    fields = {}
    for index, field in enumerate(x.split(delimiter)):

        try:
            validator = messages.MESSAGE_FORMAT_SETSmm[index]

            if validator is not None:
                validated_field = validator(field)
            else:
                validated_field = field

        except KeyError:
            raise errors.InvalidOrderFieldError(
                'Received an invalid order field(%s). ' % index
            )

        fields[
            messages.MESSAGE_FORMAT_INDEX_TO_PARAMS[index]
        ] = validated_field

    return fields


def build_order_from_ascii_string(string: str) -> Order:
    r""" Creates an order based on the "SETSmm specification.

    Parameters:
        string: an ascii encoded string representing the message

    Returns:
        Either a `LimitOrder` or `IcebergOrder`
    """

    fields = _validate_order_string(string)

    if messages.MESSAGE_FORMAT_INDEX_TO_PARAMS[4] in fields:
        return IcebergOrder.from_fields(**fields)
    else:
        return LimitOrder.from_fields(**fields)


# EOF
