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
DIFFICULTY = 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
print('Mine DIFFICULTY:', DIFFICULTY)
len("000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
# 5000000000000000000000000000000000000000000
# 22300745198530623141535718272648361505980415

import matplotlib.pyplot as plt
def visualization(blocks):
    x = range(len(blocks))
    y = [block.duration for block in blocks]
    x_standard = range(len(blocks))
    y_standard = [60 for i in x_standard]
    plt.figure(figsize=(8,4)) 
    l1=plt.plot(x,y,'r--',label='Mining')
    l2=plt.plot(x_standard,y_standard,'g--',label='Standard')
    plt.plot(x,y,'ro-',x_standard,y_standard,'g+-')
    plt.xlabel("Height")
    plt.ylabel("Time(s)")
    plt.legend()
    plt.title("Time Analysis")
    
## PID ajustment
## U(t) = Kp*error(t) + Ki*integration(error(t)) + Kd*(error(t) - error(t-1))
## Initialize kp = 1.5  Ki = 1 Kd = 1, more epochs to find the best coefficient
## target = 60s
## error(t) = 60s - real_time
## new_Diffculty = old_Diffculty + U(t)
## old_Difficulty = 5 means 00000 + FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

import math
kp = 5000000000000000000000000000000000000000
ki = 1000000000000000000000000000000000000
kd = 1000000000000000000000000000000000000
difficulties = [DIFFICULTY]
# kp = 0.5, ki = 0.2, kd = 0.1
# kp = 0.5, ki = 0.3, kd = 0.1
# kp = 0.5, ki = 0.4, kd = 0.1

def adjustmentDifficulty(old_Difficulty,height):
    old_Difficulty = math.log2(old_Difficulty)
    print("old_Difficulty:",old_Difficulty)
    ut = kp*errors[height] + ki*errors_sum + kd*(errors[height] - errors[height-1])
    print("ut:", ut) 
    new_Difficulty = old_Difficulty - ut
    print("new_Difficulty:",new_Difficulty)
    return math.pow(2,  new_Difficulty)  

def adjustmentDifficulty2(old_Difficulty,height):
    ut = kp*errors[height] + ki*errors_sum + kd*(errors[height] - errors[height-1])
    new_Difficulty = old_Difficulty - ut
    print('********************************************************')
    print('New Difficulty: ', new_Difficulty, 'Difficulty cahnge: ', ut, ' errors: ', errors[height], ' errors_sum: ', errors_sum)
    print('********************************************************')
    difficulties.append(new_Difficulty)
    return new_Difficulty

## Start mining
import random
import sys
import os
from datetime import datetime
from multiprocessing import Process, Pool, Queue, Manager

epochs = 100
blocks = []
errors = [0]
errors_sum = 0
pre_hash = '0'
height = 1
max_nounce = sys.maxsize

# 100 blocks
nodes_numbers = [0,5,12,12,15,7,8,9,12,15,13,15,4,6,8,10,7,16,13,2,4,3,12,16,5,11,13,16,14,14,6,7,
                 5,12,12,15,7,8,9,12,15,13,15,4,6,8,10,7,16,13,2,4,3,12,16,5,11,13,16,14,14,6,7,
                 5,12,12,15,7,8,9,12,15,13,15,4,6,8,10,7,16,13,2,4,3,12,16,5,11,13,16,14,14,6,7,
                 5,12,12,15,7,8,9,12,15,13,15,4,6,8,10,7,16,13,2,4,3,12,16,5,11,13,16,14,14,6,7]

def long_time_task(i, queue, start, height, pre_hash, merkle, DIFFICULTY):
#     print('Run task %s (%s)...' % (i, os.getpid()))  
    start_time = datetime.now()
    while queue.empty():
#         print("process: %s nounce: %s" % (i, start))
        block = Block(height, pre_hash, merkle, start, [])
        if int(block.getHash(),16) < DIFFICULTY:
            block.printJSON()
            queue.put(start)
            break
        else:
            start += 1
#     end_time = datetime.now()
#     duration = end_time - start_time
#     duration = duration.total_seconds()
#     print(duration)
    
while height < len(nodes_numbers):
    print('Epoch %s, Parent process %s, mining...' % (height, os.getpid()))
    merkle = sha1(random.random())
    nodes_number = nodes_numbers[height]
    unit_nounce = max_nounce // nodes_number
    p = Pool()
    queue = Manager().Queue()
    start_time = datetime.now()

    for i in range(nodes_number):
        start = i * unit_nounce # nounce
        p.apply_async(long_time_task, args = (i, queue, start, height, pre_hash, merkle, DIFFICULTY))  
    p.close()
    p.join()
    
    end_time = datetime.now()
    duration = end_time - start_time
    duration = duration.total_seconds()
    print('duration time: %s' % duration)
    
    block = Block(height, pre_hash, merkle, queue.get(True), [])
    block.duration = duration
    blocks.append(block)
    error = 60 - duration
    errors.append(error)
    errors_sum += error
    
    print('errors', errors, "errors_sum", errors_sum)
    DIFFICULTY = adjustmentDifficulty2(DIFFICULTY,height)

    height += 1
    pre_hash = block.getHash()

visualization(blocks)
print(difficulties)