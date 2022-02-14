#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Orders """


import abc
import enum
import dataclasses

from pymatch import errors, display as display_lib


class OrderSide(enum.IntEnum):

    BID = BUY = 1
    ASK = SELL = -1

    @property
    def to_display(self) -> str:
        if self is self.BID:
            return display_lib.BOOK_FORMAT_BODY_BID
        elif self is self.ASK:
            return display_lib.BOOK_FORMAT_BODY_ASK


@enum.unique
class OrderType(enum.IntEnum):

    UNKNOWN = -1
    LIMIT = 0
    MARKET = 1
    ICEBERG = 2

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
        type_: OrderType,
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

        self.type = type_
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

    @abc.abstractmethod
    def _update_display_quantity(self, matched_quantity: int) -> None:
        pass

    @property
    def display_quantity(self) -> int:
        return self.quantity

    def to_display(self, **kwargs) -> str:
        args = [self.identity, self.display_quantity, self.price]

        if self.side is OrderSide.ASK:
            args = args[::-1]

        return self.side.to_display.format(*args)


@dataclasses.dataclass(init=False, repr=False)
class LimitOrder(_BaseOrder):
    r""" Creates a limit order, a passive order that is placed onto the book
    at a specified level.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, type_=OrderType.LIMIT, **kwargs)

    def _update_display_quantity(self, matched_quantity: int) -> None:
        del matched_quantity  # unused method
        pass


@dataclasses.dataclass(init=False)
class IcebergOrder(_BaseOrder):
    r""" Creates an iceberg order, a passive order that is placed onto
    the book wherein only the "peak_size" is displayed.
    """

    def __init__(self, peak_size: int, *args, **kwargs):
        super().__init__(*args, type_=OrderType.ICEBERG, **kwargs)

        self.peak_size = self._validate_peak_size(peak_size)
        self._reset_peak_size()

    def _update_display_quantity(self, matched_quantity: int) -> int:

        if self.quantity <= self.peak_size:

            del matched_quantity

            # The total order size is less than the peak, so display the
            # remaining quantity
            return self.quantity

        if matched_quantity >= self.peak_quantity:
            # If the matched quantity is greater than the current
            # peak-quantity then we should the display the next peak size
            return self._reset_peak_size()

        # Otherwise the matched_quantity is less than the displayed peak
        # size, so reduce the displayed peak quantity
        self.peak_quantity -= matched_quantity
        return self.peak_quantity

    def _validate_peak_size(self, peak_size: int) -> int:
        if peak_size > self.quantity:
            raise errors.OrderError(
                'Received an "Iceberg" order with a peak size greater than '
                'the given size. '
            )

        return peak_size

    def _reset_peak_size(self) -> None:
        # The peak may match multiple times: used to resent the quantity back
        # to the peak size
        self.peak_quantity = self.peak_size
        return self.peak_size


# EOF
