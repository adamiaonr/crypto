# encrypted-data-computing
experiments with partially homomorphic encryption

## client/server example

as a first step, i've implemented a simple client/server experiment: a client requests x random operations to be performed on a server, and gets back the results. the objective was to compare the times of the operations over encrypted and non-encrypted data. 

### requirements

### usage



### results
**TL;DR:** as seen [here](https://github.com/adamiaonr/encrypted-data-computing/blob/master/graphs/exec-times.pdf), 'encrypted' execution times are longer by ~4 orders of magnitude (in other words, *tremendously* longer...). this is consistent with mentions in the related work of [BlindBox](http://iot.stanford.edu/pubs/sherry-blindbox-sigcomm15.pdf) or [Embark](http://www.justinesherry.com/assets/papers/embark.pdf).
