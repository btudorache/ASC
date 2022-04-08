"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Lock
from unittest import TestCase
import logging
import logging.handlers

from tema.product import Tea, Coffee


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
        # logger setup could be refactored into a method
        self.logger = logging.getLogger('marketplace_logger')
        self.logger.setLevel(logging.INFO)
        rotating_handler = logging.handlers.RotatingFileHandler('marketplace.log',
                                                                maxBytes=10000,
                                                                backupCount=10)

        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%dT%H:%M:%S')
        formatter.converter = time.gmtime
        rotating_handler.setFormatter(formatter)
        self.logger.addHandler(rotating_handler)

        self.market_lock = Lock()
        self.print_lock = Lock()

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
            self.logger.info('entering register_producer')
            producer_id = f'producer{self.producer_id_count}'
            self.producer_items_count[producer_id] = 0
            self.products[producer_id] = {}
            self.producer_id_count += 1

            self.logger.info('leaving register_producer')
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
        self.logger.info('entering publish with args: {%s}, {%s}', producer_id, str(product))
        if self.producer_items_count[producer_id] == self.queue_size:
            self.logger.info('leaving publish')
            return False

        if product.name not in self.all_products:
            self.all_products[product.name] = product

        with self.market_lock:
            self.producer_items_count[producer_id] += 1
            if product.name not in self.products[producer_id]:
                self.products[producer_id][product.name] = (1, 0)
            else:
                num_items, reserved_items = self.products[producer_id][product.name]
                self.products[producer_id][product.name] = num_items + 1, reserved_items

        self.logger.info('leaving publish')
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.market_lock:
            self.logger.info('entering new_cart')
            cart_id = f'cons{self.consumer_id_count}'
            self.carts[cart_id] = {}
            self.consumer_id_count += 1

            self.logger.info('leaving new_cart')
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
        self.logger.info('entering add_to_cart with args: {%s}, {%s}', cart_id, str(product))
        for producer_id, producer_products in self.products.items():
            if product.name in producer_products:
                num_items, reserved_items = producer_products[product.name]
                with self.market_lock:
                    if reserved_items < num_items:
                        producer_products[product.name] = (num_items, reserved_items + 1)

                        if product.name not in self.carts[cart_id]:
                            self.carts[cart_id][product.name] = {}

                        if producer_id not in self.carts[cart_id][product.name]:
                            self.carts[cart_id][product.name][producer_id] = 1
                        else:
                            self.carts[cart_id][product.name][producer_id] += 1

                        self.logger.info('leaving add_to_cart')
                        return True

        self.logger.info('leaving add_to_cart')
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info('entering remove_from_cart with args: {%s}, {%s}',
                         cart_id, str(product))
        deleted_producer_id = None
        for producer_id in self.carts[cart_id][product.name]:
            with self.market_lock:
                if self.carts[cart_id][product.name][producer_id] > 0:
                    deleted_producer_id = producer_id
                    self.carts[cart_id][product.name][producer_id] -= 1
                    if self.carts[cart_id][product.name][producer_id] == 0:
                        del self.carts[cart_id][product.name][producer_id]
                    if len(self.carts[cart_id][product.name]) == 0:
                        del self.carts[cart_id][product.name]

                    break

        if deleted_producer_id is None:
            self.logger.info('leaving remove_from_cart')
            return False

        with self.market_lock:
            num_items, reserved_items = self.products[deleted_producer_id][product.name]
            self.products[deleted_producer_id][product.name] = num_items, reserved_items - 1

        self.logger.info('leaving remove_from_cart')
        return True

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info('entering place_order with args: {%s}', cart_id)
        items_bought = []
        for product_name in self.carts[cart_id]:
            for producer_id, num_reserved in self.carts[cart_id][product_name].items():
                with self.market_lock:
                    num_items, reserved_items = self.products[producer_id][product_name]
                    self.products[producer_id][product_name] = \
                        (num_items - num_reserved, reserved_items - num_reserved)
                    self.producer_items_count[producer_id] -= num_reserved
                    for _ in range(num_reserved):
                        items_bought.append(f'{cart_id} bought {self.all_products[product_name]}')

        self.carts[cart_id] = {}

        self.logger.info('leaving place_order')
        return items_bought


class TestMarketplace(TestCase):
    """
    Class used for testing the Marketplace module.
    """
    def setUp(self):
        """
        Tests set up method
        """
        self.marketplace = Marketplace(2)
        self.first_prd_id = self.marketplace.register_producer()
        self.second_prd_id = self.marketplace.register_producer()

        self.first_cart_id = self.marketplace.new_cart()
        self.second_cart_id = self.marketplace.new_cart()

        self.fake_products = {'first_tea': Tea('Green', 2, 'Good'),
                              'second_tea': Tea('Black', 3, 'Bad'),
                              'first_coffee': Coffee('Brazilian', 5, 'high', 'high')}

    def test_register_producer(self):
        """
        register_producer test method
        """
        first_producer_id = self.marketplace.register_producer()
        self.assertEqual(first_producer_id, 'producer3')
        self.assertEqual(self.marketplace.producer_items_count[first_producer_id], 0)
        self.assertTrue(first_producer_id in self.marketplace.products)
        self.assertEqual(self.marketplace.producer_id_count, 4)

        second_producer_id = self.marketplace.register_producer()
        self.assertEqual(second_producer_id, 'producer4')
        self.assertEqual(self.marketplace.producer_id_count, 5)

    def test_publish(self):
        """
        publish test method
        """
        first_product = self.fake_products['first_tea']
        result = self.marketplace.publish(self.first_prd_id, first_product)
        self.assertEqual(result, True)
        self.assertTrue(first_product.name in self.marketplace.all_products)
        self.assertEqual(self.marketplace.products[self.first_prd_id][first_product.name], (1, 0))

        result = self.marketplace.publish(self.first_prd_id, first_product)
        self.assertEqual(result, True)
        self.assertEqual(self.marketplace.products[self.first_prd_id][first_product.name], (2, 0))

        result = self.marketplace.publish(self.first_prd_id, first_product)
        self.assertEqual(result, False)

        second_product = self.fake_products['first_coffee']
        result = self.marketplace.publish(self.second_prd_id, second_product)
        self.assertEqual(result, True)
        self.assertEqual(self.marketplace.products[self.second_prd_id][second_product.name],
                         (1, 0))

    def test_new_cart(self):
        """
        new_cart test method
        """
        first_cart_id = self.marketplace.new_cart()
        self.assertEqual(first_cart_id, 'cons3')
        self.assertTrue(first_cart_id in self.marketplace.carts)
        self.assertEqual(self.marketplace.consumer_id_count, 4)

        second_producer_id = self.marketplace.new_cart()
        self.assertEqual(second_producer_id, 'cons4')
        self.assertEqual(self.marketplace.consumer_id_count, 5)

    def test_add_to_cart(self):
        """
        add_to_cart test method
        """
        self.marketplace.publish(self.first_prd_id, self.fake_products['first_tea'])
        found_res = self.marketplace.add_to_cart(self.first_cart_id,
                                                 self.fake_products['first_tea'])
        self.assertTrue(found_res)
        self.assertEqual(self.marketplace.products[self.first_prd_id]['Green'],
                         (1, 1))
        self.assertTrue('Green' in self.marketplace.carts[self.first_cart_id])
        self.assertEqual(self.marketplace.carts[self.first_cart_id]['Green'][self.first_prd_id],
                         1)

        add_again_res = self.marketplace.add_to_cart(self.first_cart_id,
                                                     self.fake_products['first_tea'])
        self.assertFalse(add_again_res)

        self.marketplace.publish(self.first_prd_id, self.fake_products['first_tea'])
        found_again = self.marketplace.add_to_cart(self.first_cart_id,
                                                   self.fake_products['first_tea'])
        self.assertTrue(found_again)
        self.assertEqual(self.marketplace.products[self.first_prd_id]['Green'],
                         (2, 2))
        self.assertEqual(self.marketplace.carts[self.first_cart_id]['Green'][self.first_prd_id],
                         2)

    def test_remove_from_cart(self):
        """
        remove_from_cart test method
        """
        self.marketplace.publish(self.first_prd_id, self.fake_products['first_tea'])
        self.marketplace.add_to_cart(self.first_cart_id, self.fake_products['first_tea'])

        result = self.marketplace.remove_from_cart(self.first_cart_id,
                                                   self.fake_products['first_tea'])
        self.assertTrue(result)
        self.assertEqual(self.marketplace.products[self.first_prd_id]['Green'],
                         (1, 0))
        self.assertTrue('Green' not in self.marketplace.carts[self.first_cart_id])

    def test_place_order(self):
        """
        place_order test method
        """
        self.marketplace.publish(self.first_prd_id, self.fake_products['first_tea'])
        self.marketplace.publish(self.first_prd_id, self.fake_products['first_coffee'])
        self.marketplace.add_to_cart(self.first_cart_id, self.fake_products['first_tea'])
        self.marketplace.add_to_cart(self.first_cart_id, self.fake_products['second_tea'])

        items_bought = self.marketplace.place_order(self.first_cart_id)
        self.assertTrue(str(self.fake_products['first_tea']) in items_bought[0])
