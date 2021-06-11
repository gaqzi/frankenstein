#!/usr/bin/env python

from time import sleep

mod = __import__ ('mod.Order')
print mod
mod2 = getattr (mod, 'Order')
print mod2
#sleep (10)
print reload (mod2)

mod2 = getattr (mod2, 'Order')
mod2 ('hej')
print __globals__

#bara testar att lägga upp
