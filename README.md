# encrypted-data-computing
Experiments with partially homomorphic encryption

## Client & server example

As a first step, i've implemented a simple client/server experiment. 
A client requests the execution of *x* operations on a server, and checks the 
returned results. the objective was to compare the times of the operations over 
encrypted and non-encrypted data. 

For each operation, the client picks 2 floating 
point operands at random, as well as one of the following arithmetic operations, 
supported by the [Paillier cryptosystem](https://en.wikipedia.org/wiki/Paillier_cryptosystem):

* Multiplication of encrypted number by a non encrypted number
* Sum of two encrypted numbers
* Sum of an encrypted number to a non-encrypted number

### Requirements

We use a Partially Homomorphic Encryption library for Python 
([phe](http://python-paillier.readthedocs.io/en/latest/)), which can 
be installed via pip:

```
$ sudo pip install --upgrade phe
```

I had to install a bunch of system packages (e.g. via `apt-get` for Ubuntu), a 
step which wasn't explicit in phe's documentation. Also, while installing phe 
you may run into the following error:

```
byte-compiling build/bdist.linux-x86_64/egg/phe/command_line.py to command_line.pyc
  File "build/bdist.linux-x86_64/egg/phe/command_line.py", line 117
    print(serialised, file=output)
                          ^
SyntaxError: invalid syntax
```

This seems to be caused by incompatible versions of `print`. To fix, I've 
added the following line to **the top of the file**:

```
#!/usr/bin/env python3
from __future__ import print_function # the new line
```

### Usage

Open 2 terminal tabs, and start the server:
```
$  python server.py &
waiting for a connection...
```

For example, we can request a bunch (100 by default) of encrypted and non-encrypted calculations, also instructing the 
client and server to plot results:
```
$ python client.py --plot
connecting to localhost port 10000
request : 39.825915 +* 86.260188 (= 126.086103)
response_size : 2584 (/2584)
response : 39.825915 +* 86.260188 = 126.086103 (126.086103)
request : 95.927299 x* 1.612882 (= 154.719396)
response_size : 2586 (/2586)
(...)
```

The client prints times of encryption and decription (see example [here](https://github.com/adamiaonr/encrypted-data-computing/blob/master/graphs/client-times.pdf)), the server prints execution times for each type of operation (example [here](https://github.com/adamiaonr/encrypted-data-computing/blob/master/graphs/exec-times.pdf)).

### Results

**TL;DR:** as seen [here](https://github.com/adamiaonr/encrypted-data-computing/blob/master/graphs/exec-times.pdf), 
'encrypted' execution times are longer by ~4 orders of magnitude (in other 
words, *tremendously* longer...). this is consistent with mentions in the 
related work of [BlindBox](http://iot.stanford.edu/pubs/sherry-blindbox-sigcomm15.pdf) 
or [Embark](http://www.justinesherry.com/assets/papers/embark.pdf).
