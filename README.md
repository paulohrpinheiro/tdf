tdf
===

Text Data File - a module to do data persistence in python, in size fixed rows, size fixed columns, no data types.

For small data, no index.

The key for register is the number of register.

No install process, just copy the tdf.py file on your project:

---> cut here <---

import tdf

REGISTERS=10

data = tdf.Manager(filename='test.tdf', structure=(('login', 50), ('password', 50),), in_memory=True, debug=True)

with data:
    [data.append({'password': str(i), 'login': str(i)}) for i in range(0,REGISTERS)]
    [print(data[x]) for x in range(0, REGISTERS)]

data.open()
print("There are {} registers.".format(len(data)))
data.close()

---> cut here <---

See the test.py file for more extensive examples.
