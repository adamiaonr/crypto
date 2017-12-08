import sys
import argparse
import datetime as date

# custom imports
import blockchain as bc

# generate genesis block of accountability blockchain
def create_genesis_block():
  # index zero and arbitrary previous hash
  return bc.Block(0, date.datetime.now(), "genesis block", "0")

# generate all later blocks in the blockchain
def next_block(last_block):
  index = last_block.index + 1
  ts = date.datetime.now()
  data = "block " + str(index)

  # hash of new block done over hash of previous
  # blocks. once we add a block to the chain, 
  # it cannot be replaced...
  block_hash = last_block.hash

  return bc.Block(index, ts, data, block_hash)

if __name__ == "__main__":

    # use an ArgumentParser for a nice CLI
    parser = argparse.ArgumentParser()

    # options (self-explanatory)
    parser.add_argument(
        "--num-blocks", 
         help = """add <num-blocks> blocks to account_chain""")

    args = parser.parse_args()

    if not args.num_blocks:
        sys.stderr.write("""%s: [ERROR] please provide nr of blocks to add\n""" % sys.argv[0]) 
        parser.print_help()
        sys.exit(1)

    # create the accountability blockchain and add the genesis block
    account_chain = [create_genesis_block()]
    previous_block = account_chain[0]

    # Add blocks to the chain
    for i in range(0, int(args.num_blocks)):

      new_block = next_block(previous_block)
      # FIXME: if we were on a distributed setting, someone 
      # could add another new block before 'new_block' is added, 
      # which would make 'new_block' break the integrity of the 
      # account_chain
      account_chain.append(new_block)
      previous_block = new_block

      print("block %d has been added to the accountability blockchain" % (new_block.index))
      print("Hash: %s\n" % (new_block.hash))