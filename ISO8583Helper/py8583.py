#!/usr/bin/python3

FIELD_LENGTH = [
    64 // 8, 19, 6, 12, 12, 12, 10, 8,  # 1-8
    8, 8, 6, 6, 4, 4, 4, 4,  # 9-16
    4, 4, 3, 3, 3, 3, 3, 3,  # 17-24
    2, 2, 1, 1 + 8, 1 + 8, 1 + 8, 1 + 8, 11,  # 25-32
    11, 28, 37, 104, 12, 6, 2, 3,  # 33-40
    8, 15, 40, 16, 76, 999, 999, 999,  # 41-48
    3, 3, 3, 64 // 8, 16, 120, 999, 999,  # 49-56
    999, 999, 999, 999, 999, 999, 999, 64 // 8,  # 57-64
    1, 1, 2, 3, 3, 3, 4, 4,  # 65-72
    6, 10, 10, 10, 10, 10, 10, 10,  # 73-80
    10, 12, 12, 12, 12, 16, 16, 16,  # 81-88
    16, 42, 1, 2, 5, 7, 42, 64 // 8,  # 89-96
    1 + 16, 25, 11, 11, 17, 28, 28, 100,  # 97-104
    999, 999, 999, 999, 999, 999, 999, 999,  # 105-112
    999, 999, 999, 999, 999, 999, 999, 999,  # 112-120
    999, 999, 999, 999, 999, 999, 999, 64 // 8,  # 121-128
]

FIX, LLVAR, LLLVAR = 1, 2, 3
FIELD_VAR_TYPE = [
    FIX, LLVAR, FIX, FIX, FIX, FIX, FIX, FIX,  # 1-8
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, FIX,  # 9-16
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, FIX,  # 17-24
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, LLVAR,  # 25-32
    LLVAR, LLVAR, LLVAR, LLLVAR, FIX, FIX, FIX, FIX,  # 33-40
    FIX, FIX, FIX, LLVAR, LLVAR, LLLVAR, LLLVAR, LLLVAR,  # 41-48
    FIX, FIX, FIX, FIX, FIX, LLLVAR, LLLVAR, LLLVAR,  # 49-56
    LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, FIX,  # 57-64
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, FIX,  # 65-72
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, FIX,  # 73-80
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, FIX,  # 81-88
    FIX, FIX, FIX, FIX, FIX, FIX, FIX, FIX,  # 89-96
    FIX, FIX, LLVAR, LLVAR, LLVAR, LLVAR, LLVAR, LLLVAR,  # 97-104
    LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR,  # 105-112
    LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR,  # 112-120
    LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, LLLVAR, FIX,  # 121-128
]

TYPEA, TYPEN, TYPEXN, TYPES, TYPEAN, TYPEAS, TYPENS, TYPEANS, TYPEB, TYPEZ, TYPE63 = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
FIELD_TYPE = [
    TYPEB, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN,  # 1-8
    TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN,  # 9-16
    TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN,  # 17-24
    TYPEN, TYPEN, TYPEN, TYPEXN, TYPEXN, TYPEXN, TYPEXN, TYPEN,  # 25-32
    TYPEN, TYPENS, TYPEZ, TYPEN, TYPEAN, TYPEAN, TYPEAN, TYPEAN,  # 33-40
    TYPEANS, TYPEANS, TYPEANS, TYPEAN, TYPEAN, TYPEAN, TYPEAN, TYPEAN,  # 41-48
    TYPEAN, TYPEAN, TYPEAN, TYPEB, TYPEN, TYPEAN, TYPEANS, TYPEANS,  # 49-56
    TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPE63, TYPEB,  # 57-64
    TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN,  # 65-72
    TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN,  # 73-80
    TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN, TYPEN,  # 81-88
    TYPEN, TYPEN, TYPEAN, TYPEAN, TYPEAN, TYPEAN, TYPEAN, TYPEB,  # 89-96
    TYPEXN, TYPEANS, TYPEN, TYPEN, TYPEANS, TYPEANS, TYPEANS, TYPEANS,  # 97-104
    TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS,  # 105-112
    TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS,  # 112-120
    TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEANS, TYPEB,  # 121-128
]

RIGHT_JUSTIFIED, LEFT_JUSTIFIED = 0, 1
FIELD_JUSTIFIED = [
    RIGHT_JUSTIFIED, LEFT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 1-8
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 9-16
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 17-24
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 25-32
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, LEFT_JUSTIFIED, LEFT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED,  # 33-40
    LEFT_JUSTIFIED, LEFT_JUSTIFIED, RIGHT_JUSTIFIED, LEFT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED,  # 41-48
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 49-56
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 57-64
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 65-72
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 73-80
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 81-88
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 89-96
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 97-104
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 105-112
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 112-120
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,
    RIGHT_JUSTIFIED, RIGHT_JUSTIFIED,  # 121-128
]


def pack8583(dic):  # dict to byte str
    if not isinstance(dic, dict):
        raise ValueError('input type dismatch dict')

    tpdu = dic['tpdu']
    if len(tpdu) != 10:
        raise ValueError('tpdu length dismatch 10')
    del dic['tpdu']
    if isinstance(tpdu, bytes):
        tpdu = tpdu.decode()
    if not isinstance(tpdu, str):
        raise ValueError('tpdu data type dismatch bytes or str')

    msg_type = dic['msg_type']
    if len(msg_type) != 4:
        raise ValueError('msg_type length dismatch 4')
    del dic['msg_type']
    if isinstance(msg_type, bytes):
        msg_type = msg_type.decode()
    if not isinstance(msg_type, str):
        raise ValueError('msg_type data type dismatch bytes or str')

    bitmap = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    bitmap_size = len(bitmap)

    data_list = []

    field, i, j = -1, 0, 0
    while i < bitmap_size and dic != {}:
        j = 256
        while j > 1:
            j >>= 1
            field += 1
            field_name = 'field_%d' % (field + 1)
            if not dic.get(field_name):
                continue

            bitmap[i] |= j
            field_data = dic[field_name]
            if isinstance(field_data, str):
                field_data = field_data.encode()
            if not isinstance(field_data, bytes):
                raise ValueError('field %d data type dismatch bytes or str' % (field + 1))

            field_length = len(field_data)
            field_true_length = 0
            length_hex = b''

            if field_length > FIELD_LENGTH[field]:
                raise ValueError('field %d too long %d' % (field + 1, field_length))
            if FIELD_VAR_TYPE[field] == FIX:
                field_true_length = FIELD_LENGTH[field]
            elif FIELD_VAR_TYPE[field] == LLVAR:
                field_true_length = field_length
                length_hex = bytes.fromhex('%02d' % (field_true_length))
            elif FIELD_VAR_TYPE[field] == LLLVAR:
                field_true_length = field_length
                length_hex = bytes.fromhex('%04d' % (field_true_length))
            else:
                raise ValueError('field %d FIELD_VAR_TYPE no define %d' % (field + 1, FIELD_VAR_TYPE[field]))

            field_hex = b''
            if FIELD_TYPE[field] in (TYPEA, TYPES, TYPEAN, TYPEAS, TYPEANS, TYPEB):
                field_hex = field_data + (field_true_length - field_length) * b'\x00'
            elif FIELD_TYPE[field] in (TYPENS, TYPEN, TYPEZ):
                if (field_true_length % 2) == 1:
                    field_true_length += 1
                field_hex = b'0' * field_true_length
                field_hex = list(field_hex)
                field_data = list(field_data)
                if FIELD_JUSTIFIED[field] == RIGHT_JUSTIFIED:
                    field_hex[-field_length:] = field_data[:]
                elif FIELD_JUSTIFIED[field] == LEFT_JUSTIFIED:
                    field_hex[:field_length] = field_data[:]
                else:
                    raise ValueError('field %d FIELD_JUSTIFIED no define %d' % (field + 1, FIELD_JUSTIFIED[field]))
                field_hex = bytes(field_hex)
                field_data = bytes(field_data)
                field_hex = bytes.fromhex(field_hex.decode())
            elif FIELD_TYPE[field] in (TYPEXN,):
                field_hex = b'0' * (field_true_length - 1)
                field_hex = list(field_hex)
                field_data = list(field_data)
                if FIELD_JUSTIFIED[field] == RIGHT_JUSTIFIED:
                    field_hex[-(field_length - 1):] = field_data[1:]
                elif FIELD_JUSTIFIED[field] == LEFT_JUSTIFIED:
                    field_hex[:(field_length - 1)] = field_data[1:]
                else:
                    raise ValueError('field %d FIELD_JUSTIFIED no define %d' % (field + 1, FIELD_JUSTIFIED[field]))
                field_hex = bytes(field_hex)
                field_data = bytes(field_data)
                field_hex = bytes.fromhex(field_hex.decode())
                field_hex = field_data[:1] + field_hex
            else:
                raise ValueError('field %d FIELD_TYPE no define %d' % (field + 1, FIELD_TYPE[field]))
            data_list.append(length_hex + field_hex)
            del dic[field_name]
        i += 1

    if field > 63:
        bitmap[0] |= 0x80
        data_list.insert(0, bytes(bitmap[8:]))

    data_list.insert(0, bytes(bitmap[:8]))
    data_list.insert(0, bytes.fromhex(msg_type))
    data_list.insert(0, bytes.fromhex(tpdu))
    data_list.insert(0, bytes.fromhex(len(b''.join(data_list))))
    data = b''.join(data_list)
    return data


def unpack8583(data):  # byte str to dict
    if not isinstance(data, bytes):
        raise ValueError('input type dismatch bytes')

    dic = {}
    index = 0
    data_len = len(data)

    if index + 2 > data_len:
        raise ValueError('data len length to short')
    dic['data_len'] = data[index:index + 2].hex().encode()
    index += 2

    if index + 5 > data_len:
        raise ValueError('tpdu length to short')
    dic['tpdu'] = data[index:index + 5].hex().encode()
    index += 5

    if index + 2 > data_len:
        raise ValueError('msg_type length to short')
    dic['msg_type'] = data[index:index + 2].hex().encode()
    index += 2

    if index + 8 > data_len:
        raise ValueError('bitmap length to short')
    bitmap = data[index:index + 8]
    dic['bitmap'] = bitmap
    index += 8
    if (bitmap[0] & 128) == 128 and index + 8 <= data_len:
        bitmap += data[index:index + 8]
    bitmap_size = len(bitmap)

    field, i, j = -1, 0, 0
    while i < bitmap_size:
        j = 256
        while j > 1:
            j >>= 1
            field += 1
            if bitmap[i] & j == 0:
                continue
            field_data = b''
            field_length = 0

            if FIELD_VAR_TYPE[field] == FIX:
                field_length = FIELD_LENGTH[field]
            elif FIELD_VAR_TYPE[field] == LLVAR:
                if index + 1 > data_len:
                    raise ValueError('field %d length to short' % (field + 1))
                field_length = (int)(data[index:index + 1].hex())
                if field_length > FIELD_LENGTH[field]:
                    raise ValueError('field %d length to long %d' % (field + 1, field_length))
                index += 1
            elif FIELD_VAR_TYPE[field] == LLLVAR:
                if index + 2 > data_len:
                    raise ValueError('field %d length to short' % (field + 1))
                field_length = (int)(data[index:index + 2].hex())
                if field_length > FIELD_LENGTH[field]:
                    raise ValueError('field %d length to long %d' % (field + 1, field_length))
                index += 2
            # elif FIELD_VAR_TYPE[field] == FIELD63:
            #     field_length = data_len - index
            else:
                raise ValueError('field %d FIELD_VAR_TYPE no define %d' % (field + 1, FIELD_VAR_TYPE[field]))

            if FIELD_TYPE[field] in (TYPEA, TYPES, TYPEAN, TYPEAS, TYPEANS, TYPEB):
                if index + field_length > data_len:
                    raise ValueError('field %d to short %d' % (field + 1, FIELD_TYPE[field], field_length))
                if field + 1 == 44:
                    dic['field_%d' % (field + 1)] = data[index:index + field_length].hex().encode()
                else:
                    dic['field_%d' % (field + 1)] = data[index:index + field_length]
                index += field_length
            elif FIELD_TYPE[field] in (TYPENS, TYPEN, TYPEZ):
                field_length_tmp = (field_length + 1) // 2
                if index + field_length_tmp > data_len:
                    raise ValueError('field %d to short %d' % (field + 1, field_length_tmp))
                if FIELD_JUSTIFIED[field] == RIGHT_JUSTIFIED:
                    dic['field_%d' % (field + 1)] = data[index:index + field_length_tmp].hex().encode()[-field_length:]
                elif FIELD_JUSTIFIED[field] == LEFT_JUSTIFIED:
                    dic['field_%d' % (field + 1)] = data[index:index + field_length_tmp].hex().encode()[:field_length]
                else:
                    raise ValueError('field %d FIELD_JUSTIFIED no define %d' % (field + 1, FIELD_JUSTIFIED[field]))
                index += field_length_tmp
                pass
            elif FIELD_TYPE[field] in (TYPEXN,):
                field_length_tmp = field_length // 2
                if index + 1 + field_length_tmp > data_len:
                    raise ValueError('field %d to short %d' % (field + 1, 1 + field_length_tmp))
                dic['field_%d' % (field + 1)] = data[index:index + 1] + data[
                                                                        index + 1:index + 1 + field_length_tmp].hex().encode()
                index += (1 + field_length_tmp)
            elif FIELD_TYPE[field] in (TYPE63,):
                dic['field_%d' % (field + 1)] = data[index:index + field_length]
                index += field_length
                unpackField_63(dic)
            else:
                raise ValueError('field %d FIELD_TYPE no define %d' % (field + 1, FIELD_TYPE[field]))
        i += 1

    if dic.get('field_1'):
        del dic['field_1']

    return dic

def unpackField_63(dic):
    field_63 = dic['field_63']
    Tag = ''
    Length = 0
    Value = ''
    index = 0

    while index < len(field_63):
        Tag = field_63[index: index + 1].hex()
        index += 1
        Length = (int)(field_63[index: index + 1].hex())
        index += 1
        Value = field_63[index: index + Length]
        dic['field_63_' + Tag] = Value
        index += Length
    return dic

def comm(ip, port, sendData):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    s.connect((ip, port))

    sendLen = len(sendData)
    sendData = sendLen.to_bytes(length=2, byteorder='big', signed=False) + sendData
    s.send(sendData)

    recvLen = s.recv(2)
    if len(recvLen) == 0:
        raise ValueError('recv length close by peer')
    if len(recvLen) != 2:
        raise ValueError('recv length format error')

    recvLen = int.from_bytes(recvLen, byteorder='big', signed=False)
    recvData = s.recv(recvLen)
    if len(recvData) == 0:
        raise ValueError('recv data close by peer')
    if len(recvData) != recvLen:
        raise ValueError('recv data format error')

    s.close()
    return recvData


if __name__ == '__main__':
    # sale
    dic = {'tpdu': '6056781234',
           'msg_type': '0200',
           'field_2': '6200000000000000000',
           'field_3': '000000',
           'field_4': '1000',
           'field_11': '1',
           'field_22': '032',
           'field_25': '00',
           'field_41': '00000001',
           'field_42': '000000000000001',
           'field_49': '344',
           'field_64': '1234567',
           'field_65': '1',
           'field_66': '2',
           }

    for i in list(dic.keys()):
        print('{0}:{1}'.format(i, dic[i]))

    data = pack8583(dic)
    print('data:', data)

    dic = unpack8583(data)
    for i in list(dic.keys()):
        print('{0}:{1}'.format(i, dic[i]))

    data = pack8583(dic)
    print('data:', data)
    print('------------------------------------------')

    recvData = b'\x60\x56\x78\x12\x34\x02\x00\xff\xff\xff\xff\xff\xff\xff\xe3\xc0\x00\x00\x00\x00\x00\x00\x00\x05\x22\x22\x20\x33\x33\x33\x00\x00\x00\x00\x04\x44\x00\x00\x00\x00\x05\x55\x00\x00\x00\x00\x06\x66\x00\x00\x00\x07\x77\x00\x00\x08\x88\x00\x00\x09\x99\x00\x00\x00\x00\x00\x00\x11\x22\x22\x22\x33\x33\x44\x44\x55\x55\x66\x66\x77\x77\x88\x88\x09\x99\x00\x00\x00\x11\x02\x22\x03\x33\x04\x44\x55\x66\x07\x38\x00\x00\x08\x88\x39\x00\x00\x09\x99\x30\x00\x00\x00\x00\x31\x00\x00\x00\x01\x06\x22\x22\x22\x04\x33\x33\x04\x44\x44\x04\x55\x55\x00\x04\x66\x66\x37\x37\x37\x37\x37\x37\x37\x37\x37\x37\x37\x37\x38\x38\x38\x38\x38\x00\x39\x39\x30\x30\x30\x31\x31\x31\x31\x31\x31\x31\x31\x32\x32\x32\x32\x32\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x04\x34\x34\x34\x34\x04\x35\x35\x35\x35\x00\x04\x36\x36\x36\x36\x00\x04\x37\x37\x37\x37\x00\x04\x38\x38\x38\x38\x39\x39\x39\x30\x30\x30\x31\x31\x31\x00\x00\x32\x32\x32\x32\x32\x32\x00\x00\x00\x00\x00\x00\x33\x33\x00\x04\x34\x34\x34\x34\x00\x04\x35\x35\x35\x35\x00\x04\x36\x36\x36\x36\x00\x04\x37\x37\x37\x37\x00\x04\x38\x38\x38\x38\x00\x04\x39\x39\x39\x39\x00\x08\x33\x33\x33\x33\x33\x33\x33\x33\x31\x31\x31\x31\x31\x31\x31\x31\x01\x02'
    dic = unpack8583(recvData)
    print("recv")
    for i in list(dic.keys()):
        print('{0}:{1}'.format(i, dic[i]))
    print('------------------------------------------')
