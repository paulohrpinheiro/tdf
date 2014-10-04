import os.path
import inspect

class Manager(object):
    """
    Manage a text data file, with fixed lenght registers.
    """

    def __init__(self, filename, structure, in_memory=False, debug=False):
        """
        Initialize internal elements.
        The structucture parameter is a tuple of fieldnames and lengths,
        like this: (('name', 10), ('pass', 50), ('date', 8)). 
        Note: '#' fieldname is reserved, raise an error.
        if 'in_memory' is True, also put all data into memory.
        """

        self.__filename = filename
        self.__register_structure = structure
        self.__in_memory = in_memory
        self.debug = debug

        self.__register_length = sum(info[1] for info in self.__register_structure)
        self.__register_mask = ''.join(['{%s:<%d}'%(x[0],x[1]) for x in self.__register_structure])
        self.__register_fieldnames = [x[0] for x in self.__register_structure]

        self.__buffer_size = None

    def __dump_function_info(self, *data):
        """
        helper to print debug info.
        """

        if not self.debug:
            return

        current_frame = inspect.currentframe()
        calling_frame = inspect.getouterframes(current_frame, 2)
        calling_function_name = calling_frame[1][3]

        print(calling_function_name, end='')
        [print('({}): {}'.format(type(x), x, end=' ')) for x in data]
        print()

    def open(self):
        """
        Try open data file.
        """

        open_file_function = lambda: open(self.__filename, 'r+')

        try:
            self.__fh = open_file_function()
        except IOError:
            try:
                with open(self.__filename, 'a'):
                    pass
            except e:
                raise ErrorCreateFile(e)
            else:
                self.__fh = open_file_function()
        except Exception as e:
            raise ErrorUnknow(e)

        if self.__in_memory:
            self.__read_all_content()

    def __read_all_content(self):
        """
        Try put all data into memory.
        """

        # in open,  we don't have self.__data, then don't have len(self)
        self.__data = [self.__getitemfromfile(x) for x in range(0, self.__registers())]

    def __enter__(self):
        """
        To use in with statment.
        """

        self.open()

    def close(self):
        """
        Finish use of this file.
        """

        self.__fh.close()

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        """
        To use in with statment.
        """

        self.close()

    def __address(self, register_number):
        """
        Return initial position of a register in file.
        """

        return (register_number * self.__register_length)

    def __current_address(self):
        """
        Return current position in data file.
        """

        return (self.__fh.tell())

    def __current_register_number(self):
        """
        Return current register number, based in current file position.
        """

        _current_position = self.__current_address()
        _length = self.__register_length
        _current_register = int(_current_position/_length)

        self.__dump_function_info(_current_position, _length, _current_register)

        return (_current_register)

    def __seek(self, register_number):
        """
        Go to file pos of register_number.
        """

        _address = self.__address(register_number)

        self.__dump_function_info(_address)

        self.__fh.seek(_address, 0)

    def __pack(self, unpacked_data):
        """
        Get a dictionary and transform in a packed string.
        """

        self.__dump_function_info(self.__register_mask, unpacked_data)
        return self.__register_mask.format(**unpacked_data)

    def __unpack(self, packed_data):
        """
        Put 'packed' data on a dictionary.
        """

        position = 0
        unpacked_data = {}

        for register_name, register_length in self.__register_structure:
            last_position = position + register_length
            unpacked_data[register_name] = packed_data[position:last_position].rstrip()
            position = last_position

        return (unpacked_data)

    def flush(self):
        """
        Call I/O library flush function.
        """

        self.__fh.flush()

    def __write(self, register_data):
        """
        Write register_data to file.
        """

        self.__fh.write(self.__pack(register_data))

    def next(self):
        """
        Advance one registar, if possible.
        """

        self.__fh.seek(self.__register_length, 1)

    def prev(self):
        """
        Recue one register, if possible.
        """

        self.__fh.seek(self.__register_length*-1, 1)

    def __goto_file_begin(self):
        """
        Go to begin of file.
        """
		
        self.__fh.seek(0, 0)

    def __goto_file_end(self):
        """
        Go to end of file.
        """

        self.__fh.seek(0, 2)

    def append(self, register_data):
        """
        Append a register into file.
        """

        self.__fh.seek(0,2)
        self.__write(register_data)
        _current = self.__current_register_number()-1

        if self.__in_memory:
            self.__data.append(register_data)
            assert len(self) == len(self.__data)

        self.__dump_function_info(_current)

        return(_current)

    def __setitem__(self, register_number, register_data):
        """
        Save existent register.
        """

        self.__dump_function_info()

        self.__seek(register_number)
        self.__write(register_data)

        if self.__in_memory:
            self.__data[register_number] = register_data

    def __registers(self):
        """
        Return total of register, based on file size.
        """

        self.__goto_file_end()
        total_registers = self.__current_register_number()

        return(total_registers)

    def __len__(self):
        """
        Return total of registers in file.
        """

        if self.__in_memory:
            total_registers = len(self.__data)
        else:
            total_registers = self.__registers(x)

        return(total_registers)

    def __getitemfromfile(self, register_number):
        """
        Return, from file, data of register_number.
        """

        self.__seek(register_number)
        packed_data = self.__fh.read(self.__register_length)
        unpacked_data = self.__unpack(packed_data)
        register_data = unpacked_data
        register_data['#'] = register_number

        return(register_data)

    def __getitem__(self, register_number):
        """
        Return data of register_number.
        """

        if self.__in_memory:
            register_data = self.__data[register_number]
        else:
            register_data = self.__getfromfile(register_number)

        self.__dump_function_info(self.__in_memory, register_data)

        return (register_data)

    def __iter__(self):
        """
        Return a iterator.
        """

        if not self.__in_memory:
            self.__goto_file_begin()

        for i in range(len(self)):
            yield self.__getitem__(i)


class ErrorBase(Exception):
    """
    Base class to error handling
    """

    def __init__(self, my_message, system_message):
        """ Print error message """

        _dump_function_info('%s: [%s].'%(my_message, system_message))


class ErrorUnknow(ErrorBase):
    def __init__(self, system_message):
        super().__init__( 'Unknow error', system_message)


class ErrorOpenFile(ErrorBase):
    def __init__(self, system_message):
        super().__init__('Cannot open file', system_message)


class ErrorCreateFile(ErrorBase):
    def __init__(self, system_message):
        super().__init__('Cannot create file', system_message)


if '__main__' == __name__:
    print(Manager.__doc__)
    print(dir(Manager))

