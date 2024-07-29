from future.utils import viewitems
from future.utils import viewvalues
from future.utils import viewkeys
from future.utils import iteritems
from future.utils import itervalues
from future.utils import iterkeys
tel = {'jack': 4098, 'sape': 4139, 'guido': 4127}

keyiter = iterkeys(tel)
valueiter = itervalues(tel) 
itemiter = iteritems(tel) 

for key in iterkeys(tel):
    pass
for value in itervalues(tel):
    pass
for (key,value) in iteritems(tel):
    pass 

keyview = viewkeys(tel)
valueview = viewvalues(tel) 
itemview = viewitems(tel) 

for key in viewkeys(tel):
    pass
for value in viewvalues(tel):
    pass
for (key,value) in viewitems(tel):
    pass 

keylist = list(tel.keys())
valuelist = list(tel.values()) 
itemlist = list(tel.items()) 

for key in tel.keys():
    pass
for value in tel.values():
    pass
for (key,value) in tel.items():
    pass 