#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

# TODO(dreiss): Test error cases.  Check for memory leaks.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
from DebugProtoTest import Srv
from DebugProtoTest.ttypes import *
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import sys
import timeit

if sys.version_info[0] >= 3:
    from io import BytesIO
    StringIO = BytesIO
else:
    from cStringIO import StringIO
from copy import deepcopy
from pprint import pprint

class TDevNullTransport(TTransport.TTransportBase):
    def __init__(self):
        pass
    def isOpen(self):
        return True

reserved = Reserved()
reserved.from_PY_RESERVED_KEYWORD = "reserved"

ooe1 = OneOfEach()
ooe1.im_true   = True
ooe1.im_false  = False
ooe1.a_bite    = 0xd6
ooe1.integer16 = 27000
ooe1.integer32 = 1<<24
ooe1.integer64 = 6000 * 1000 * 1000
ooe1.double_precision = math.pi
ooe1.some_characters  = b"Debug THIS!"
ooe1.zomg_unicode     = "\xd7\n\a\t".encode("utf-8")

ooe2 = OneOfEach()
ooe2.integer16 = 16
ooe2.integer32 = 32
ooe2.integer64 = 64
ooe2.double_precision = (math.sqrt(5)+1)/2
ooe2.some_characters  = b":R (me going \"rrrr\")"
ooe2.zomg_unicode     = "\xd3\x80\xe2\x85\xae\xce\x9d\x20"\
                        "\xd0\x9d\xce\xbf\xe2\x85\xbf\xd0\xbe"\
                        "\xc9\xa1\xd0\xb3\xd0\xb0\xcf\x81\xe2\x84\x8e"\
                        "\x20\xce\x91\x74\x74\xce\xb1\xe2\x85\xbd\xce\xba"\
                        "\xc7\x83\xe2\x80\xbc".encode("utf-8")

hm = HolyMoley(big=[], contain=set(), bonks={})
hm.big.append(ooe1)
hm.big.append(ooe2)
hm.big[0].a_bite = 0x22
hm.big[1].a_bite = 0x22

hm.contain.add((b"and a one", b"and a two"))
hm.contain.add((b"then a one, two", b"three!", "FOUR!"))
hm.contain.add(())

hm.bonks[b"nothing"] = []
hm.bonks[b"something"] = [
    Bonk(type=1, message=b"Wait."),
    Bonk(type=2, message=b"What?"),
]
hm.bonks[b"poe"] = [
    Bonk(type=3, message=b"quoth"),
    Bonk(type=4, message=b"the raven"),
    Bonk(type=5, message=b"nevermore"),
]

rs = RandomStuff()
rs.a = 1
rs.b = 2
rs.c = 3
if sys.version_info[0] >= 3:
    rs.myintlist = list(range(20))
else:
    rs.myintlist = range(20)
rs.maps = {1:Wrapper(foo=Empty()), 2:Wrapper(foo=Empty())}
rs.bigint = 124523452435
rs.triple = 3.14

# make sure this splits two buffers in a buffered protocol
rshuge = RandomStuff()
if sys.version_info[0] >= 3:
    rshuge.myintlist = list(range(10000))
else:
    rshuge.myintlist = range(10000)

my_zero = Srv.Janky_result(5)

def checkWrite(o):
    trans_fast = TTransport.TMemoryBuffer()
    trans_slow = TTransport.TMemoryBuffer()
    prot_fast = TBinaryProtocol.TBinaryProtocolAccelerated(trans_fast)
    prot_slow = TBinaryProtocol.TBinaryProtocol(trans_slow)

    o.write(prot_fast)
    o.write(prot_slow)
    ORIG = trans_slow.getvalue()
    MINE = trans_fast.getvalue()
    if ORIG != MINE:
        print("mine: %s\norig: %s" % (repr(MINE), repr(ORIG)))

def checkRead(o):
    prot = TBinaryProtocol.TBinaryProtocol(TTransport.TMemoryBuffer())
    o.write(prot)

    slow_version_binary = prot.trans.getvalue()

    prot = TBinaryProtocol.TBinaryProtocolAccelerated(
           TTransport.TMemoryBuffer(slow_version_binary))
    c = o.__class__()
    c.read(prot)
    if c != o:
        print("copy: ")
        pprint(eval(repr(c)))
        print("orig: ")
        pprint(eval(repr(o)))

    prot = TBinaryProtocol.TBinaryProtocolAccelerated(
            TTransport.TBufferedTransport(
                TTransport.TMemoryBuffer(slow_version_binary)))
    c = o.__class__()
    c.read(prot)
    if c != o:
        print("copy: ")
        pprint(eval(repr(c)))
        print("orig: ")
        pprint(eval(repr(o)))


def doTest():
    checkWrite(hm)
    no_set = deepcopy(hm)
    no_set.contain = set()
    checkRead(no_set)
    checkRead(reserved)
    checkWrite(reserved)
    checkWrite(rs)
    checkRead(rs)
    checkWrite(rshuge)
    checkRead(rshuge)
    checkWrite(my_zero)
    checkRead(my_zero)
    checkRead(Backwards(first_tag2=4, second_tag1=2))

    # One case where the serialized form changes, but only superficially.
    o = Backwards(first_tag2=4, second_tag1=2)
    trans_fast = TTransport.TMemoryBuffer()
    trans_slow = TTransport.TMemoryBuffer()
    prot_fast = TBinaryProtocol.TBinaryProtocolAccelerated(trans_fast)
    prot_slow = TBinaryProtocol.TBinaryProtocol(trans_slow)

    o.write(prot_fast)
    o.write(prot_slow)
    ORIG = trans_slow.getvalue()
    MINE = trans_fast.getvalue()
    if ORIG == MINE:
        print("That shouldn't happen.")


    prot = TBinaryProtocol.TBinaryProtocolAccelerated(
            TTransport.TMemoryBuffer())
    o.write(prot)
    prot = TBinaryProtocol.TBinaryProtocol(TTransport.TMemoryBuffer(
            prot.trans.getvalue()))
    c = o.__class__()
    c.read(prot)
    if c != o:
        print("copy: ")
        pprint(eval(repr(c)))
        print("orig: ")
        pprint(eval(repr(o)))



def doBenchmark():

    iters = 25000

    setup = """
from __main__ import hm, rs, TDevNullTransport
from thrift.protocol import TBinaryProtocol
trans = TDevNullTransport()
prot = TBinaryProtocol.TBinaryProtocol%s(trans)
"""

    setup_fast = setup % "Accelerated"
    setup_slow = setup % ""

    print("Starting Benchmarks")

    print("HolyMoley Standard = %f" %
        timeit.Timer('hm.write(prot)', setup_slow).timeit(number=iters))
    print("HolyMoley Acceler. = %f" %
        timeit.Timer('hm.write(prot)', setup_fast).timeit(number=iters))

    print("FastStruct Standard = %f" %
        timeit.Timer('rs.write(prot)', setup_slow).timeit(number=iters))
    print("FastStruct Acceler. = %f" %
        timeit.Timer('rs.write(prot)', setup_fast).timeit(number=iters))


if __name__ == "__main__":
    doTest()
    doBenchmark()

