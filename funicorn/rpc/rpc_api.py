from thrift.server import TNonblockingServer
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport
from funicorn.rpc.FunicornService import Processor
from funicorn.logger import get_logger
from funicorn.utils import colored_network_name
import threading
import time
import json


class Handler():
    def __init__(self, funicorn_app, stat, logger):
        self.funicorn_app = funicorn_app
        self.stat = stat
        self.logger = logger

    def predict_img_bytes(self, img_bytes):
        start_time = time.time()
        assert isinstance(img_bytes, bytes)
        json_result = self.funicorn_app.predict(img_bytes)
        self.stat.increment('total_req')
        if isinstance(json_result, str) or isinstance(json_result, dict):
            ValueError('The result from rpc must be json string')
        self.logger.debug(f'process-time: {time.time() - start_time}')
        self.stat.increment('total_res')
        return json.dumps(json_result)


class ThriftAPI(threading.Thread):
    def __init__(self, funicorn_app, host, port, name='RPC', stat=None, threads=40,
                 timeout=1000, debug=False):
        threading.Thread.__init__(self, daemon=True)
        self.name = name
        self.funicorn_app = funicorn_app
        self.host = host
        self.port = port
        self.stat = stat
        self.threads = threads
        self.debug = debug
        self.logger = get_logger(colored_network_name(
            'RPC'), mode='debug' if debug else 'info')
        self.funicorn_app.register_connection(self)

    def init_connection(self, processor):
        '''
        Initialize all connections with TBinaryProtocol and TFramedTransport

        Parameters
        ----------
        processor : TProcessor
            Processor class has been generated by thrift

        Returns
        -------
        server: TServer
            TNonblocking Server
        '''
        socket = TSocket.TServerSocket(host=self.host, port=self.port)
        prot_fac = TBinaryProtocol.TBinaryProtocolFactory()
        server = TNonblockingServer.TNonblockingServer(processor=processor,
                                                       lsocket=socket,
                                                       inputProtocolFactory=prot_fac,
                                                       threads=self.threads)
        return server

    def init_handler(self):
        return Handler(self.funicorn_app, self.stat, self.logger)

    def init_processor(self, handler):
        processor = Processor(handler)
        return processor

    def run(self):
        handler = self.init_handler()
        processor = self.init_processor(handler)
        server = self.init_connection(processor)
        self.logger.info(
            f'Server is running at http://{self.host}:{self.port}')
        server.serve()
