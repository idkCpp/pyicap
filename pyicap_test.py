#!/bin/env python
# -*- coding: utf8 -*-

import random
import SocketServer

from pyicap import *

class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass

class ICAPHandler(BaseICAPRequestHandler):

    def echo_options(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Service', 'Vengit ICAP Server 1.0')
        self.set_icap_header('Preview', '0')
        self.set_icap_header('Transfer-Preview', '*')
        self.set_icap_header('Transfer-Ignore', 'jpg,jpeg,gif,png,swf,flv')
        self.set_icap_header('Transfer-Complete', '')
        self.set_icap_header('Max-Connections', '100')
        self.set_icap_header('Options-TTL', '3600')
        self.send_headers(False)
        self.log_request(200)

    def echo_respmod(self):
        self.set_icap_response(200)

        self.set_enc_status(' '.join(self.enc_res_status))
        for h in self.enc_res_headers:
            for v in self.enc_res_headers[h]:
                self.set_enc_header(h, v)

        # The code below is only copying some data.
        # Very convoluted for such a simple task.
        # This thing needs a serious redesign.
        # Well, without preview, it'd be quite simple...
        if not self.has_body:
            self.send_headers(False)
            self.log_request(200)
            return
        if self.preview:
            prevbuf = ''
            while True:
                # TODO: is this appropriate? How much we can write here?
                chunk = self.read_chunk()
                if chunk == '':
                    break
                prevbuf += chunk
            if self.ieof:
                self.send_headers(True)
                if len(prevbuf) > 0:
                    self.write_chunk(prevbuf)
                self.write_chunk('')
                self.log_request(200)
                return
            self.cont()
            self.send_headers(True)
            if len(prevbuf) > 0:
                self.write_chunk(prevbuf)
            while True:
                chunk = self.read_chunk()
                self.write_chunk(chunk)
                if chunk == '':
                    break
        else:
            self.send_headers(True)
            while True:
                chunk = self.read_chunk()
                self.write_chunk(chunk)
                if chunk == '':
                    break

        self.log_request(200)

port = 13440

server = ThreadingSimpleServer(('', port), ICAPHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print "Finished"
