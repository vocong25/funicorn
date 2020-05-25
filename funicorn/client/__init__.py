import time
import sys
import cv2
import numpy as np
from ..rpc.ttypes import *
from ..rpc import FunicornService
from ..utils import (img_bytes_to_img_arr,
                     img_arr_to_img_bytes,
                     get_logger,
                     colored_worker_name)
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.transport import TTransport, TSocket


class Client():
    '''Simple Client for Funicorn'''

    def __init__(self, port, host='0.0.0.0', timeout_ms=1000, debug=False, asynchronous=False):
        self.host = host
        self.port = port
        self.transport = None
        self.client = None
        self.asynchronous = asynchronous
        self.results = {}
        self.logger = get_logger(colored_worker_name('CLIENT'),
                                 mode='debug' if debug else 'info')

    def get_connection(self):
        '''Get new connection'''
        socket = TSocket.TSocket(self.host, self.port)
        transport = TTransport.TFramedTransport(socket)
        protocol = TBinaryProtocol(transport)
        client = FunicornService.Client(protocol)
        transport.open()
        return client, transport

    def __enter__(self):
        self.client, self.transport = self.get_connection()
        self.logger.debug('Initialize new connection!')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transport.isOpen():
            self.logger.debug('Connection closed!')
            self.transport.close()

    def preinit_connection(self):
        if self.client is None:
            self.client, self.transport = self.get_connection()

    def predict_img_arr(self, img_arr):
        self.preinit_connection()
        img_bytes = img_arr_to_img_bytes(img_arr)
        return self.client.predict_img_bytes(img_bytes)

    def predict_img_bytes(self, img_bytes):
        self.preinit_connection()
        return self.client.predict_img_bytes(img_bytes)

    def ping(self):
        self.preinit_connection()
        return self.client.ping()

    def close(self):
        if self.transport.isOpen():
            self.transport.close()