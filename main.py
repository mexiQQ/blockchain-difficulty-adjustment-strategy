###########################################################
###########################################################
###########################################################

## 自变量 挖矿节点 难度目标
## 因变量 出块时间

## 目标：找到一组合适的 PID 参数，使得每挖一个块，做一次难度调节
##      使得连续生成 1000 个块的方差较小
##      多组PID参数做比较 原始难度调整策略做比较

## 使用hash算法 sha1, 一共 160位，难度前导0最多159位

## 目标挖矿平均时间 60s， 记录每个新块的产生时间

## CPU: 2.3 GHz Intel Core i9, 8 - core, use muti-process to simulate the mining nodes

## the root hash of merkle tree is selected by random.

###########################################################
###########################################################
###########################################################

## Support Functions
import hashlib
def sha1(obj: str):
    return hashlib.sha1(str(obj).encode('utf-8')).hexdigest()

## Block
class Block:
    duration = 0
    
    def __init__(self, height, pre_hash, merkle, nouce, transactions):
        self.height = height
        self.pre_hash = pre_hash
        self.merkle = merkle
        self.nouce = nouce
        self.transactions = transactions

    def getHash(self):
        return sha1(self)
    
    def __repr__(self):
        return str(self.pre_hash) + str(self.height) + str(self.merkle) + str(self.nouce)
    
    def printJSON(self):
        # DFS or BFS
        print("Hash:", self.getHash(), "Height:", self.height, "Pre_Hash:", self.pre_hash, "Merkle Hash:", self.merkle, "nouce:", self.nouce)
        pass

## mine difficaulty
## 40 - 4 = 36
## hash value should smaller than DIFFICULTY
DIFFICULTY = 0x000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
print('Mine DIFFICULTY:', DIFFICULTY)
len("000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")

## Start mining
import random
import sys
import os
from datetime import datetime
from multiprocessing import Process, Pool, Queue, Manager

epochs = 100
blocks = []
errors = []
errors_sum = 0
pre_hash = '0'
height = 1
max_nounce = sys.maxsize

# 100 blocks
nodes_numbers = [12,12,15,19,18,30,12,34,23,25,32,32,36,37,32,33,33,41,45,55,44,33,22,24,25,25,26,26,26,29,
                 12,12,15,19,19,30,12,34,23,25,32,32,36,37,32,33,33,41,45,55,44,33,22,24,25,25,26,26,26,29,
                 12,12,15,19,19,30,12,34,23,25,32,32,36,37,32,33,33,41,45,55,44,33,22,24,25,25,26,26,26,29,
                 12,12,15,19,19,30,12,34,23,25]

def long_time_task(i, queue, start, height, pre_hash, merkle, target):
#     print('Run task %s (%s)...' % (i, os.getpid()))  
    start_time = datetime.now()
    while queue.empty():
#         print("process: %s nounce: %s" % (i, start))
        block = Block(height, pre_hash, merkle, start, [])
        if int(block.getHash(),16) < target:
            block.printJSON()
            queue.put(start)
            break
        else:
            start += 1
#     end_time = datetime.now()
#     duration = end_time - start_time
#     duration = duration.total_seconds()
#     print(duration)
    
while height <= len(nodes_numbers):
    print('Epoch %s, Parent process %s, mining...' % (height, os.getpid()))
    merkle = sha1(random.random())
    nodes_number = nodes_numbers[height]
    unit_nounce = max_nounce // nodes_number
    p = Pool(nodes_number)
    q = Manager().Queue()
    start_time = datetime.now()

    for i in range(nodes_number):
        start = i * unit_nounce # nounce
        p.apply_async(long_time_task, args = (i, q, start, height, pre_hash, merkle, DIFFICULTY))  
    p.close()
    p.join()
    
    end_time = datetime.now()
    duration = end_time - start_time
    duration = duration.total_seconds()
    print('duration time: %s' % duration)
    
    block = Block(height, pre_hash, merkle, q.get(True), [])
    block.duration = duration
    blocks.append(block)
    errors.append(60 - duration)
    errors_sum += duration

    height += 1
    pre_hash = block.getHash()