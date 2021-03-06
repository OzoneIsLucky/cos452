#!/usr/local/pypy-1.6/bin/pypy

import sys


def main():
    total_bits = 0
    bits_set = 0

    while True:
        block = sys.stdin.read(2 ** 19)
        if not block:
            break
        total_bits += len(block) * 8
        # print('got block of length %d' % len(block))
        for char in block:
            byte = ord(char)
            # print('got char %d' % byte)
            for exponent in range(8):
                bitmask = 2 ** exponent
                # print('checking mask %d' % bitmask)
                if byte & bitmask != 0:
                    # print('adding 1 to count')
                    bits_set += 1

    print(
        '%s set, %s present, %6.2f%%' % (
            bits_set,
            total_bits,
            bits_set * 100.0 / total_bits,
        )
    )


if __name__ == '__main__':
    main()
