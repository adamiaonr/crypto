import socket
import sys
import json # for the app level protocol
import argparse
import random
import fcntl, os
import errno
import thread
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math

from collections import defaultdict
from phe import paillier # for hpe operations
from pprint import pprint 
from signal import signal, SIGINT

processing_times = defaultdict()
sock = None

def signal_handler(signal, frame):
    sock.close()
    sys.exit(0)

# register SIGINT callback
signal(SIGINT, signal_handler)

def process_request(request, public_key_rec = None):

    # prepare the response
    response = {}
    response['type'] = 'response'
    response['mode'] = request['mode']
    response['public_key'] = request['public_key']
    response['operation']  = request['operation']

    if request['mode'] == 'encrypted':

        if public_key_rec is None:
            print('unloading public key')
            public_key = request['public_key']
            public_key_rec = paillier.PaillierPublicKey(g = int(public_key['g']),
                                                        n = int(public_key['n']))

        print('unloading encrypted operand')
        operand_1 = paillier.EncryptedNumber(public_key_rec, int(request['operand_1'][0]), int(request['operand_1'][1]))

        # if operation is plain addition, encrypt the 2nd operand too 
        if request['operation'] == '+':
            operand_2 = paillier.EncryptedNumber(public_key_rec, int(request['operand_2'][0]), int(request['operand_2'][1]))
        else:
            operand_2 = float(request['operand_2'])

        # the actual operation
        print('performing operation %s' % (request['operation']))
        if request['operation'] == 'x*':
            result = operand_1 * operand_2
        else:
            result = operand_1 + operand_2

        response['result'] = (str(result.ciphertext()), result.exponent)

    else:

        if '+' in request['operation']:
            result = float(request['operand_1']) + float(request['operand_2'])
        else:
            result = float(request['operand_1']) * float(request['operand_2'])

        response['result'] = (str(result))

    return response

def handle_client(sock, client_address):

    while True:

        try:

            request = ''
            request_size = 1

            while len(request) < request_size:

                # keep buffering the request
                request += sock.recv(4096)

                # extract the request size
                if '\r\n' in request:
                    request_size_str = request.split('\r\n', 1)[0]
                    request_size = len(request_size_str) + 2 + int(request_size_str)

                else:
                    request_size = len(request) + 1

                print('request_size : %d (/%d)' % (request_size, len(request)))

            print('server::handle_client() : unloading json')
            request = json.loads(request.split('\r\n', 1)[1])

            if request['type'] == 'terminate':

                print('server::handle_client() : terminating...')
                # close the socket
                sock.close()
                return

            elif request['type'] == 'plot':

                print_graph(processing_times)
                sock.close()
                return

            else:

                mode = request['mode']
                operation = request['operation']

                if mode not in processing_times:
                    processing_times[mode] = defaultdict()

                if operation not in processing_times[mode]:
                    processing_times[mode][operation] = []

                start_time = time.time()
                response = process_request(request, public_key_rec)
                processing_times[mode][operation].append(time.time() - start_time)

                response_body = json.dumps(response)
                response_body_len = len(response_body)

                print('server::handle_client() : sending response (%d)' % (response_body_len))
                sock.sendall(str(response_body_len) + '\r\n' + response_body)

        except socket.error, e:
            print('server::handle_client() : error occurred: %s. aborting.' % (e))
            sock.close()
            return

def print_graph(data):

    fig = plt.figure(figsize=(10, 4))

    i = 1
    for mode in ['encrypted', 'unencrypted']:

        ax1 = fig.add_subplot(120 + i)
        ax1.set_title(mode)
        ax1.yaxis.grid(True)

        xtick_labels = ['sum', 'sum w/ scalar', 'mult. w/ scalar']

        n = 0.0
        for k in data[mode]:
            if max(data[mode][k]) > n:
                n = max(data[mode][k])
                print('server::print_graph() : %f (%d)' % (n, int(math.log10(n))))    

        log_n = int(math.log10(n))
        for k in data[mode]:
            data[mode][k] = [ (v / math.pow(10, log_n)) for v in data[mode][k] ]

        values = [
            data[mode]['+'], 
            data[mode]['+*'], 
            data[mode]['x*']
        ]

        ax1.boxplot(values, 0, '')

        xticks = [1, 2, 3]
        ax1.set_xticks(xticks)
        ax1.set_xticklabels(xtick_labels)
        ax1.set_xticklabels(ax1.xaxis.get_majorticklabels(), rotation=45)
        ax1.set_xlabel("Operations")
        ax1.set_ylabel("Execution time ($10^{%s}$ sec)" % (log_n))

        i = i + 1

    fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3, hspace=None)
    plt.savefig("../graphs/exec-times.pdf", bbox_inches='tight', format = 'pdf')

if __name__ == "__main__":

    public_key_rec = None

    # create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock can now re-bind to port in use (we always use port 10000). it 
    # makes sense in our case, since we'll start/terminate/start the server 
    # a lot of times during testing...
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the port
    server_address = ('localhost', 10000)

    print('starting up on %s port %s' % (server_address))
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)

    while True:

        try:
            # wait for a connection
            print('waiting for a connection...')

            connection, client_address = sock.accept()
            print('connection from %s' % (client_address[0]))
            thread.start_new_thread(handle_client, (connection, client_address))

        except socket.error, e:
            print('error occurred: %s. aborting.' % (e))
            sock.close()
            sys.exit(1)

    sock.close()
    sys.exit(0)
