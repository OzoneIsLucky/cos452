# Author: Owen Elliott
# COS452: Research 1 Project

import bloomfilter

class bloomFilterObject:
    def __init__(self, item_count, fp_prob):
        self.item_count = item_count
        self.fp_prob = fp_prob
        self.item_list = []
        self.filter = bloomfilter.BloomFilter(self.item_count, self.fp_prob)
    
    def getSize(self):
        return self.filter.get_size(self.item_count, self.fp_prob)
    
    def getHashCount(self):
        return self.filter.get_hash_count(self.getSize(), self.item_count)
    
    def getBitarray(self):
        return str(self.filter.bit_array)[10:-2]
    
    def getItemList(self):
        return self.item_list

    def add(self, val, verbose=False):
        if verbose and self.item_count <= len(self.item_list):
            print("warning: exceeded expected item count")
        if verbose:
            print("adding val: " + str(val))
        val_to_bytes = int(val).to_bytes(8, 'big')
        self.filter.add(val_to_bytes)
        self.item_list.append(val)

    def check(self, val):
        val_to_bytes = int(val).to_bytes(8, 'big')
        return self.filter.check(val_to_bytes)

def checkRange(filter: bloomFilterObject, start: int, stop: int):
    for i in range(start, stop):
        print("checking val: " + str(i) + " " + str(filter.check(i)))

def testFalsePositiveProb(filter: bloomFilterObject, start: int):
    # usage: start should be larger than the largest item stored in the filter
    fp_count = 0
    for i in range(start, start + 10000):
        if filter.check(i):
            fp_count += 1
    print("fp_rate: " + str(float(fp_count / 10000)))

def testFilter(item_count, fp_prob):
    print("demonstration 1: standard use case")
    smaller_item_count = item_count // 10000
    larger_fp_prob = fp_prob * 20
    print("creating filter with item_count = " + str(smaller_item_count) + " fp_prob = " + str(larger_fp_prob))
    myFilter = bloomFilterObject(smaller_item_count, larger_fp_prob)
    print("bitarray size: " + str(myFilter.getSize()))
    print("hash func count: " + str(myFilter.getHashCount()))
    print("current bitarray:")
    print(myFilter.getBitarray())
    myFilter.add(1, verbose=True)
    print("current bitarray:")
    print(myFilter.getBitarray())
    for i in range(2, smaller_item_count):
        myFilter.add(i, verbose=True)
    print("current bitarray:")
    print(myFilter.getBitarray())
    checkRange(myFilter, 1, smaller_item_count + 25)

    print("\n")

    print("demonstration 2: exceeding item count")
    print("creating filter with item_count = " + str(item_count) + " fp_prob = " + str(fp_prob))
    myFilter3 = bloomFilterObject(item_count, fp_prob)
    print("bitarray size: " + str(myFilter3.getSize()))
    print("hash func count: " + str(myFilter3.getHashCount()))
    print("fp_rate with bloom filter at 0% capacity")
    testFalsePositiveProb(myFilter3, item_count + 1)
    for i in range(1, item_count // 2):
        myFilter3.add(i)
    print("fp_rate with bloom filter at 50% capacity")
    testFalsePositiveProb(myFilter3, item_count + 1)
    for i in range(item_count // 2, item_count):
        myFilter3.add(i)
    print("fp_rate with bloom filter at 100% capacity")
    testFalsePositiveProb(myFilter3, item_count + 1)
    for i in range(item_count, item_count * 2):
        myFilter3.add(i)
    print("fp_rate with bloom filter at 200% capacity")
    testFalsePositiveProb(myFilter3, item_count * 2 + 1)
    
testFilter(1000000, 0.01)