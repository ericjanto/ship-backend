def intToVByte(x):
    if x == 0:
        return bytearray([128])
    vBytes = []
    while x > 0:
        vBytes.append(x % 128)
        x = x >> 7
    vBytes[0] += 128 

    return bytearray(vBytes[::-1])

def vByteArrayToInts(vBytes):
    ints = [0]
    for vb in vBytes:
        val = int(vb)
        ints[-1] += val % 128
        if val >= 128:
            ints.append(0)
        else:
            ints[-1] = ints[-1] << 7
    return ints[:-1]



if __name__ == "__main__":
    print(intToVByte(150))
    print(vByteArrayToInts(intToVByte(150)))


    for i in range(1000000):
        if i != vByteArrayToInts(intToVByte(i))[0]:
            print(f"ERROR: {i}")
