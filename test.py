#!/usr/bin/env python3
    
import pprint

def assert_size(title, expected_size, class_instance):
    print('-->', title, '<--')
    print('\t', end='')
    _real_size = len(class_instance)
    print('\t','Expected:', expected_size, 'Existent:', _real_size)
    assert expected_size == _real_size

test_filename = 'user.tdf'
total_test_registers = 9999
user = Manager(filename=test_filename, structure=(('login', 9), ('password', 50),), in_memory=True, debug=False)
login_mask = 'login%04d'
password_mask = 'pass for user%05d'

try:
    os.unlink(test_filename)
except:
    pass

with user:
    assert_size('BEGIN', expected_size=0, class_instance=user)
    [user.append({'login': login_mask%x, 'password': password_mask%x}) for x in range(0, total_test_registers)]
    assert_size('POPULATED', expected_size=total_test_registers, class_instance=user)

with user:
    assert_test = lambda i: \
        int(register['#'])==i and \
        register['login']==login_mask%i and \
        register['password']==password_mask%i

    for i in range(0, len(user)):
        register = user[i]
        print(register)
        assert assert_test(i)

    assert_size('END READ', expected_size=total_test_registers, class_instance=user)

    [pprint.pprint(u) for u in user]

    for i in range(len(user)-1, 0 , -1):
        print(i, end='')
        register = user[i]
        user[i] = register

    assert_size('END WRITE', expected_size=total_test_registers, class_instance=user)

    for i in range(0, len(user)):
        register = user[i]
        assert assert_test(i)

    assert_size('END RE-READ', expected_size=total_test_registers, class_instance=user)

user.close()
with user:
    user.open()
    print(user._Manager__data)

