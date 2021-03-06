#!/usr/bin/python
# coding=utf-8

# pylint: disable=superfluous-parens
# superfluous-parens: Parentheses are good for clarity and portability

"""Unit tests for bloom_filter_mod"""

import dbm
import math
import os
import random
import sys
import time
import unittest

import bloom_filter2


CHARACTERS = 'abcdefghijklmnopqrstuvwxyz1234567890'


class States(object):
    """Generate the USA's state names"""

    def __init__(self):
        pass

    states = """Alabama Alaska Arizona Arkansas California Colorado Connecticut
        Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas
        Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota
        Mississippi Missouri Montana Nebraska Nevada NewHampshire NewJersey
        NewMexico NewYork NorthCarolina NorthDakota Ohio Oklahoma Oregon
        Pennsylvania RhodeIsland SouthCarolina SouthDakota Tennessee Texas Utah
        Vermont Virginia Washington WestVirginia Wisconsin Wyoming""".split()

    @staticmethod
    def generator():
        """Generate the states"""
        for state in States.states:
            yield state

    @staticmethod
    def within(value):
        """Is the value in our list of states?"""
        return value in States.states

    @staticmethod
    def length():
        """What is the length of our contained values?"""
        return len(States.states)


def random_string():
    """Generate a random, 10 character string - for testing purposes"""
    list_ = []
    for _ in range(10):
        character = CHARACTERS[int(random.random() * len(CHARACTERS))]
        list_.append(character)
    return ''.join(list_)


class Random_content(object):
    """Generated a bunch of random strings in sorted order"""

    random_content = [random_string() for dummy in range(1000)]

    def __init__(self):
        pass

    @staticmethod
    def generator():
        """Generate all values"""
        for item in Random_content.random_content:
            yield item

    @staticmethod
    def within(value):
        """Test for membership"""
        return value in Random_content.random_content

    @staticmethod
    def length():
        """How many members?"""
        return len(Random_content.random_content)


class Evens(object):
    """Generate a bunch of even numbers"""

    def __init__(self, maximum):
        self.maximum = maximum

    def generator(self):
        """Generate all values"""
        for value in range(self.maximum):
            if value % 2 == 0:
                yield str(value)

    def within(self, value):
        """Test for membership"""
        try:
            int_value = int(value)
        except ValueError:
            return False

        if int_value >= 0 and int_value < self.maximum and int_value % 2 == 0:
            return True
        else:
            return False

    def length(self):
        """How many members?"""
        return int(math.ceil(self.maximum / 2.0))


def give_description(filename):
    """
    Return a description of the filename type

    Could be array, file or hybrid.
    """
    if filename is None:
        return 'array'
    elif isinstance(filename, tuple):
        if filename[1] == -1:
            return 'mmap'
        else:
            return 'hybrid'
    else:
        return 'seek'


class TestBloomFilter(unittest.TestCase):
    def _test(
        self,
        description, values, trials, error_rate,
        probe_bitnoer=None, filename=None,
    ):
        # pylint: disable=R0913,R0914
        # R0913: We want a few arguments
        # R0914: We want some local variables too.  This is just test code.
        """Some quick automatic tests for the bloom filter class"""
        if not probe_bitnoer:
            probe_bitnoer = bloom_filter2.get_filter_bitno_probes

        divisor = 100000

        bloom = bloom_filter2.BloomFilter(
            max_elements=values.length() * 2,
            error_rate=error_rate,
            probe_bitnoer=probe_bitnoer,
            filename=filename,
            start_fresh=True,
        )

        message = '\ndescription: %s num_bits_m: %s num_probes_k: %s\n'
        filled_out_message = message % (
            description,
            bloom.num_bits_m,
            bloom.num_probes_k,
        )

        sys.stdout.write(filled_out_message)

        print('starting to add values to an empty bloom filter')
        for valueno, value in enumerate(values.generator()):
            reverse_valueno = values.length() - valueno
            if reverse_valueno % divisor == 0:
                print('adding valueno %d' % reverse_valueno)
            bloom.add(value)

        print('testing all known members')
        include_in_count = sum(
            include in bloom
            for include in values.generator()
        )
        self.assertEqual(include_in_count, values.length())

        print('testing random non-members')
        false_positives = 0
        for trialno in range(trials):
            if trialno % divisor == 0:
                print(
                    'trialno progress: %d / %d' % (trialno, trials),
                    file=sys.stderr,
                )
            while True:
                candidate = ''.join(random.sample(CHARACTERS, 5))
                # If we accidentally found a member, try again
                if values.within(candidate):
                    continue
                if candidate in bloom:
                    # print('false positive: %s' % candidate)
                    false_positives += 1
                break

        actual_error_rate = float(false_positives) / trials

        self.assertLess(
            actual_error_rate, error_rate,
            "Too many false positives: actual: %s, expected: %s" % (
                actual_error_rate,
                error_rate,
            ),
        )

        bloom.close()

    def test_and(self):
        """Test the & operator"""

        abc = bloom_filter2.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['a', 'b', 'c']:
            abc += character

        bcd = bloom_filter2.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['b', 'c', 'd']:
            bcd += character

        abc &= bcd

        self.assertNotIn('a', abc)
        self.assertIn('b', abc)
        self.assertIn('c', abc)
        self.assertNotIn('d', abc)

        abc.close()
        bcd.close()

    def test_or(self):
        """Test the | operator"""

        abc = bloom_filter2.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['a', 'b', 'c']:
            abc += character

        bcd = bloom_filter2.BloomFilter(max_elements=100, error_rate=0.01)
        for character in ['b', 'c', 'd']:
            bcd += character

        abc |= bcd

        self.assertIn('a', abc)
        self.assertIn('b', abc)
        self.assertIn('c', abc)
        self.assertIn('d', abc)
        self.assertNotIn('e', abc)

        abc.close()
        bcd.close()

    def test_states(self):
        self._test('states', States(), trials=100000, error_rate=0.01)

    def test_random(self):
        self._test('random', Random_content(), trials=10000, error_rate=0.1)
        self._test('random', Random_content(), trials=1000000, error_rate=1E-9)
        self._test('random', Random_content(), trials=10000, error_rate=0.1,
                   probe_bitnoer=bloom_filter2.get_bitno_seed_rnd)

        filename = 'bloom-filter-rm-me'
        self._test(
            'random',
            Random_content(),
            trials=10000,
            error_rate=0.1,
            filename=filename,
        )

    @unittest.skipUnless(os.environ.get('TEST_PERF', ''), "disabled")
    def test_performance(self):
        """Unit tests for BloomFilter class"""

        sqrt_of_10 = math.sqrt(10)
        for exponent in range(19):  # it's a lot, but probably not unreasonable
            elements = int(sqrt_of_10 ** exponent + 0.5)
            for filename in [
                None,
                'bloom-filter-rm-me',
                ('bloom-filter-rm-me', 768 * 2 ** 20),
                ('bloom-filter-rm-me', -1),
            ]:
                description = give_description(filename)
                key = '%s %s' % (description, elements)
                with dbm.open('performance-numbers', 'c') as database:
                    if key in database.keys():
                        continue
                if elements >= 100000000 and description == 'seek':
                    continue
                if elements >= 100000000 and description == 'mmap':
                    continue
                if elements >= 1000000000 and description == 'array':
                    continue
                time0 = time.time()
                self._test(
                    'evens %s elements: %d' % (
                        give_description(filename),
                        elements,
                    ),
                    Evens(elements),
                    trials=elements,
                    error_rate=1e-2,
                    filename=filename,
                )
                time1 = time.time()
                delta_t = time1 - time0
                # file_ = open('%s.txt' % description, 'a')
                # file_.write('%d %f\n' % (elements, delta_t))
                # file_.close()
                with dbm.open('performance-numbers', 'c') as database:
                    database[key] = '%f' % delta_t

    def test_probe_count(self):
        # test prob count ok
        bloom = bloom_filter2.BloomFilter(1000000, error_rate=.99)
        self.assertEqual(bloom.num_probes_k, 1)

        bloom.close()


if __name__ == '__main__':
    unittest.main()
