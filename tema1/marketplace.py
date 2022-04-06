"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""


from threading import Lock
from unittest import TestCase
from product import Tea, Coffee


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.market_lock = Lock()

        self.queue_size = queue_size_per_producer
        self.producer_items_count = {}
        self.consumer_id_count = 1
        self.producer_id_count = 1

        self.products = {}
        self.carts = {}

        self.all_products = {}

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.market_lock:
            producer_id = f'producer{self.producer_id_count}'
            self.producer_items_count[producer_id] = 0
            self.products[producer_id] = {}
            self.producer_id_count += 1

            return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        with self.market_lock:
            if self.producer_items_count[producer_id] == self.queue_size:
                return False

            if product.name not in self.all_products:
                self.all_products[product.name] = product

            self.producer_items_count[producer_id] += 1
            if product.name not in self.products[producer_id]:
                self.products[producer_id][product.name] = (1, 0)
            else:
                num_items, reserved_items = self.products[producer_id][product.name]
                self.products[producer_id][product.name] = num_items + 1, reserved_items
            return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.market_lock:
            cart_id = f'cons{self.consumer_id_count}'
            self.carts[cart_id] = {}
            self.consumer_id_count += 1

            return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        with self.market_lock:
            for producer_id, producer_products in self.products.items():
                if product.name in producer_products:
                    num_items, reserved_items = producer_products[product.name]
                    if reserved_items < num_items:
                        producer_products[product.name] = (num_items, reserved_items + 1)

                        if product.name not in self.carts[cart_id]:
                            self.carts[cart_id][product.name] = {}

                        if producer_id not in self.carts[cart_id][product.name]:
                            self.carts[cart_id][product.name][producer_id] = 1
                        else:
                            self.carts[cart_id][product.name][producer_id] += 1

                        return True

            return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        with self.market_lock:
            deleted_producer_id = None
            for producer_id in self.carts[cart_id][product.name]:
                if self.carts[cart_id][product.name][producer_id] > 0:
                    deleted_producer_id = producer_id
                    self.carts[cart_id][product.name][producer_id] -= 1
                    if self.carts[cart_id][product.name][producer_id] == 0:
                        del self.carts[cart_id][product.name][producer_id]
                    if len(self.carts[cart_id][product.name]) == 0:
                        del self.carts[cart_id][product.name]

                    break

            num_items, reserved_items = self.products[deleted_producer_id][product.name]
            self.products[deleted_producer_id][product.name] = num_items, reserved_items - 1

            return True

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        with self.market_lock:
            for product_name in self.carts[cart_id]:
                for producer_id, num_reserved in self.carts[cart_id][product_name].items():
                    num_items, reserved_items = self.products[producer_id][product_name]
                    self.products[producer_id][product_name] = \
                        (num_items - num_reserved, reserved_items - num_reserved)
                    self.producer_items_count[producer_id] -= num_reserved
                    for _ in range(num_reserved):
                        print(f'{cart_id} bought {str(self.all_products[product_name])}')

            self.carts[cart_id] = {}
