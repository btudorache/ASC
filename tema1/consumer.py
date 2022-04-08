"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.marketplace = marketplace
        self.carts = carts
        self.retry_wait_time = retry_wait_time
        self.cart_id = self.marketplace.new_cart()

    def run(self):
        for cart in self.carts:
            for operation in cart:
                op_type = operation['type']
                product = operation['product']
                quantity = operation['quantity']
                while True:
                    op_res = self.marketplace.add_to_cart(self.cart_id, product) \
                                if op_type == 'add' \
                                else self.marketplace.remove_from_cart(self.cart_id, product)

                    if op_res:
                        quantity -= 1
                    else:
                        sleep(self.retry_wait_time)

                    if quantity == 0:
                        break

            items_bought = self.marketplace.place_order(self.cart_id)
            if len(items_bought) > 0:
                with self.marketplace.print_lock:
                    print('\n'.join(items_bought))
