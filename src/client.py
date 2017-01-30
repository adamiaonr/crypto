import socket
import sys
import json # for the app level protocol
import argparse
import random
import fcntl, os
import errno
import time

from collections import defaultdict
from phe import paillier # for hpe operations
from pprint import pprint 

processing_times = defaultdict(list)

# generate public and private key
public_key, private_key = paillier.generate_paillier_keypair()

# supported operations in paillier cryptosystem:
#   'x*' : encrypted numbers can be multiplied by a non encrypted scalar
#   '+'  : encrypted numbers can be added together 
#   '+*' : encrypted numbers can be added to non encrypted scalars
operations = ['x*', '+', '+*']

def get_expected_result(operand_1, operand_2, operation):

    if operation == 'x*':
        return operand_1 * operand_2
    else:
        return operand_1 + operand_2

def generate_random_request(mode = 'encrypted'):

    # client request to send to server encoded in json
    message = {}
    message['type'] = 'request'
    message['mode'] = mode

    # in the paillier cryptosystem, a public key is a base g and modulus n
    message['public_key'] = {'g': public_key.g, 'n': public_key.n}

    # pick an operation at random
    operation = random.choice(operations)
    message['operation'] = operation

    # pick 2 operands at random
    operand_1 = random.uniform(0.0, 100.0)
    operand_2 = random.uniform(0.0, 100.0)
    expected_result = get_expected_result(operand_1, operand_2, operation)

    if mode == 'encrypted':
        # send the encrypted operands (operand 1 is encrypted for sure, operand 
        # 2 depends on the operation)
        start_time = time.time()
        encrypted_operand_1 = public_key.encrypt(operand_1)
        processing_times['encrypt'].append(time.time() - start_time)
        message['operand_1'] = (str(encrypted_operand_1.ciphertext()), encrypted_operand_1.exponent)

        # if operation is plain addition, encrypt the 2nd operand too 
        if operation == '+':
            start_time = time.time()
            encrypted_operand_2 = public_key.encrypt(operand_2)
            processing_times['encrypt'].append(time.time() - start_time)
            message['operand_2'] = (str(encrypted_operand_2.ciphertext()), encrypted_operand_2.exponent)
        else:
            message['operand_2'] = str(operand_2)

    else:
        message['operand_1'] = str(operand_1)
        message['operand_2'] = str(operand_2)

    # return the unencrypted operands and message contents
    return operand_1, operand_2, expected_result, message

if __name__ == "__main__":

    # use an ArgumentParser for a nice CLI
    parser = argparse.ArgumentParser()

    # options (self-explanatory)
    parser.add_argument(
        "--mode", 
         help = """'encrypted' or 'unencrypted'""")

    parser.add_argument(
        "--plot", 
         help = """plot a graph""")

    args = parser.parse_args()

    if not args.mode:
        args.mode = 'encrypted'

    # create a tpc/ip socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print('connecting to %s port %s' % (server_address))
    sock.connect(server_address)

    # set socket to non-blocking mode
    # fcntl.fcntl(sock, fcntl.F_SETFL, os.O_NONBLOCK)

    # run some requests on the server and time it
    for i in xrange(100):

        try:
            
            # generate a random request
            operand_1, operand_2, expected_result, body = generate_random_request(args.mode)
            print('request : %f %s %f (= %f)' % (operand_1, body['operation'], operand_2, expected_result))

            # send the message
            body = json.dumps(body)
            body_len = len(body)
            sock.sendall(str(body_len) + '\r\n' + body)

            response = ''
            response_size = 1

            while len(response) < response_size:

                # keep buffering the response
                response += sock.recv(4096)

                # extract the response size
                if '\r\n' in response:
                    response_size_str = response.split('\r\n', 1)[0]
                    response_size = len(response_size_str) + 2 + int(response_size_str)

                else:
                    response_size = len(response) + 1

                print('response_size : %d (/%d)' % (response_size, len(response)))

            response = json.loads(response.split('\r\n', 1)[1])

            if args.mode == 'encrypted':

                encrypted_result = paillier.EncryptedNumber(public_key, 
                                                            int(response['result'][0]), 
                                                            int(response['result'][1]))

                start_time = time.time()
                result = private_key.decrypt(encrypted_result)
                processing_times['decrypt'].append(time.time() - start_time)

                print('response : %f %s %f = %f (%f)' % (operand_1, response['operation'], operand_2, result, expected_result))

            else:

                result = float(response['result'])
                print('response : %f %s %f = %f (%f)' % (operand_1, response['operation'], operand_2, result, expected_result))

            if result != expected_result:
                processing_times['wrong'].append(1)
            else:
                processing_times['correct'].append(1)


        except socket.error, e:

            err = e.args[0]

            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                print 'no data available. carry on.'
                continue

            else:
                print('error occurred : %s. aborting.' % (e))
                sock.close()
                sys.exit(1)

    if args.plot:

        plot = {}
        plot['type'] = 'plot'
        plot['mode'] = args.mode

        body = json.dumps(plot)
        body_len = len(body)
        sock.sendall(str(body_len) + '\r\n' + body)
    else:
        # terminate the connection
        terminate = {}
        terminate['type'] = 'terminate'
        terminate['mode'] = args.mode

        body = json.dumps(terminate)
        body_len = len(body)
        sock.sendall(str(body_len) + '\r\n' + body)
        
    sock.close()
