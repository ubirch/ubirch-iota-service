from iota import Iota
from ubirch.anchoring import *
import random

args = set_arguments("IOTA")
depth = args.depth
uri = args.uri
api = Iota(uri)


def generate_address():
    """
        Function used to generate a new IOTA address.
        We only need one IOTA address to make the service work

        New addresses must be generated using this function and then passed as arguments in the CLI

        :return: A valid IOTA address
        :rtype <class 'iota.types.Address'>

    """
    gna_result = api.get_new_addresses(count=1)
    addresses = gna_result['addresses']
    return addresses[0]


print("new address = %s" % generate_address())


chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'  # Used to generate the seed


# Seed generator

def generate_seed():
    seed = ''
    for i in range(81): seed += random.choice(chars)
    return seed


print("new seed = %s " % generate_seed())
