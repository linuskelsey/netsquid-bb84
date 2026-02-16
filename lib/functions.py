
import numpy as np

import netsquid as ns
from netsquid.qubits.operators import Operator,create_rotation_op
from netsquid.components.instructions import *
from netsquid.components.qprogram import *
from netsquid.components.qprocessor import *
from netsquid.qubits.qubitapi import assign_qstate
from random import randint

'''
import logging
logging.basicConfig(level=logging.ERROR)
mylogger = logging.getLogger(__name__)
'''



'''
A function used to model fibre loss after keys were formed in QKD protocols.
This is used to avoid messing up with algorithm of QKD when qubits were loss.
Default loss parameter values are based on NetSquid.
input:
    key1: One of the key formed due to QKD.
    key2: One of the key formed due to QKD.
    numNodes: Number of nodes in this QLine
    fibreLen: Total fibre length ofQuantum channel.(km) (take integer)
    iniLoss: The initial loss rate which applys when qubit enters a fibre.
    lenLoss: The loss rate which applys when qubits went through a fibre per 1 km.
    algorithmFator: In average how many qubits are needed to form one key bit. In BB84 is 2.

output:
    Two proccesed keys which will likely be shorter than key1 and key2.
'''
def ManualFibreLossModel(key1,key2,numNodes,fibreLen=0,iniLoss=0.2,lenLoss=0.25,algorithmFator=2):   
    keyLen=len(key1)

    lossCount=0
    # lenLoss part
    if fibreLen != 0:
        for i in range(int(fibreLen)):
            for j in range(keyLen):
                myrand=randint(0,100)
                if myrand < lenLoss*100:
                    lossCount += 1 #loss case

    # iniLoss part
    for i in range(numNodes-1):
        myrand=randint(0,100)
        if myrand < iniLoss*100:
            lossCount += 1 #loss case

    #print('lossCount:',lossCount)
    lossCount/=algorithmFator

    if lossCount>=keyLen:
        return [],[]
    else:
        newkey1=key1[:keyLen-int(lossCount)]
        newkey2=key2[:keyLen-int(lossCount)]
        return newkey1,newkey2




'''
bitFlipNoice function to flip a bit for simulating classical noice.
input:
    bit: bit to be operated.
    f0: [0-1] One of function parameter. 0.95 means 95% chance of keeping value.
    f1:[0-1] One of function parameter.  0.995 means 99.5% chance of keeping value.
    randomInteger:[1,100].

output:
    return the bit.
'''
def bitFlipNoice(bit,f0,f1,randomInteger):
    if not bit:
        if randomInteger<=(f0*100):
            return 0
        else:
            return 1
    else:                     #bit == 1:
        if randomInteger<=(f1*100):
            return 1
        else:
            return 0



'''
Simply returns a list with 0 or 1 in given length.
'''
def Random_basis_gen(length):
    return [randint(0,1) for i in range(length)]



'''
Compare two lists, find the unmatched index, 
    then remove corresponding slots in loc_meas.
Input:
    loc_basis_list: local basis used for measuring qubits.(list of int)
    rem_basis_list: remote basis used for measuring qubits.(list of int)
        Two lists with elements 0-2 (Z,X, -1:qubit missing).
        Two lists to compare.
        
    loc_meas: Local measurement results to keep.(list of int)
Output:
    measurement result left.
'''

def Compare_basis(loc_basis_list,rem_basis_list,loc_res):

    if len(loc_basis_list) != len(rem_basis_list): #should be  len(num_bits)
        print("Comparing error! length of basis does not match!")
        return -1
    
    popList=[]
    
    for i in range(len(rem_basis_list)):
        if loc_basis_list[i] != rem_basis_list[i]:
            popList.append(i)
    
    for i in reversed(popList): 
        if loc_res:
            loc_res.pop(i)
        
    return loc_res

'''
To check which qubits are lost in given qubit list.

input:
qList(list of qubits): A qubit list, which might loss some of the qubits. 
bound(list of two int): A list of 2 value, indicating the first and last index of the ideal qubit list. 
[1,3] means the qubit list should only be qubits with index 1,2,3.

output:
A list of index, indicating which qubits are lost.
[1,5] means first and 5th qubit are lost, indicator starts by 1.(no value below 1 allowed)
'''

def CheckLoss(qList,bound):
    RemainList=[]
    for i in range(len(qList)):
        RemainList.append(int(qList[i].name[13:-len('-')-1]))    # get index from bits
    
    #print("remaining list num_inx: ",RemainList)
    
    completeList=[i for i in range(bound[0],bound[1]+1)]
    #print("completeList: ",completeList)
    
    res=[item for item in completeList if item not in RemainList]
    #print("res: ",res)
    
    return res



'''
bitFlipNoise function to flip a bit for simulating classical noise.
input:
    bit: bit to be operated.
    f0: [0-1] One of function parameter. 0.95 means 95% chance of keeping value.
    f1:[0-1] One of function parameter.  0.995 means 99.5% chance of keeping value.
    randomInteger:[1,100].

output:
    return the bit.
'''
def bitFlipNoise(bit,f0,f1,randomInteger):
    if not bit:
        if randomInteger<=(f0*100):
            return 0
        else:
            return 1
    else:                     #bit == 1:
        if randomInteger<=(f1*100):
            return 1
        else:
            return 0




'''
Assign certain quantum states to bubits.
input:
    qList: The qubit list to operate on.
    dmList: The density matrix to assign.
output:
    qList: qubit list which are assgined with given states.
'''
def AssignStatesBydm(qList,dmList):
    if len(qList)!=len(dmList):
        print("Error! List length does not match!")
        return 1
    for i,j in enumerate(qList):
        #print("F qList[0]:",qList[i],"dmList[0]:",dmList[i])
        assign_qstate(qList[i], dmList[i], formalism=ns.qubits.QFormalism.DM) #ns.qubits.QFormalism.DM

    return qList






'''
Prepare EPR pairs using qubits in this quantum processor.
input:
    pairs: how many pairs to prepare.

'''
# General functions/Quantum programs 

class PrepareEPRpairs(QuantumProgram):
    
    def __init__(self,pairs=1):
        self.pairs=pairs
        super().__init__()
        
    def program(self):
        qList_idx=self.get_qubit_indices(2*self.pairs)
        # create multiEPR
        for i in range(2*self.pairs):
            if i%2==0:                           # List A case
                self.apply(INSTR_H, qList_idx[i])
            else:                                # List B case
                self.apply(INSTR_CNOT, [qList_idx[i-1], qList_idx[i]])
        yield self.run(parallel=False)

 

'''
General measurement function.
Measure the qubits hold by this processor by basisList.
input:
    basisList: List of int, 0 means standard basis, others means Hadamard basis
'''

class QMeasure(QuantumProgram):
    def __init__(self,basisList):
        self.basisList=basisList
        super().__init__()

    def program(self):
        #print("in QMeasure")
        for i,item in enumerate(self.basisList):
            if  item== 0:  # basisList 0:Z  , 1:X
                self.apply(INSTR_MEASURE, 
                    qubit_indices=i, output_key=str(i),physical=True) 
            elif item== 1:                              
                self.apply(INSTR_MEASURE_X, 
                    qubit_indices=i, output_key=str(i),physical=True)

        yield self.run(parallel=False)


'''
General measurement function by position.
Measure the qubits hold by this processor by basisList.
Used for measure part of the qubits in Qmemory.
input:
    basisList: List of int, 0 means standard basis, others means Hadamard basis.
    position: List of int, qubits position index.
'''

class QMeasureByPosition(QuantumProgram):
    def __init__(self,basisList,position):
        self.basisList=basisList
        self.position=position
        super().__init__()

    def program(self):
        if len(self.basisList)!=len(self.position):
            print("QMeasureByPosition Error! List length does not match!")

        for i,item in enumerate(self.basisList):
            if  item== 0:  # basisList 0:Z  , 1:X
                self.apply(INSTR_MEASURE, 
                    qubit_indices=self.position[i], output_key=str(self.position[i]),physical=True) 
            elif item== 1:                              
                self.apply(INSTR_MEASURE_X, 
                    qubit_indices=self.position[i], output_key=str(self.position[i]),physical=True)

        yield self.run(parallel=False)





'''
Swap the qubits hold by this processor by position.
input:
    position:list of int: indecate qubits to swap 

'''

class QSwap(QuantumProgram):
    def __init__(self,position):
        self.position=position
        super().__init__()
        if len(position)!=2:
            print("Error parameters in QSwap!")
        

    def program(self):
        self.apply(INSTR_SWAP, qubit_indices=self.position, physical=True)
        yield self.run(parallel=False)    




'''
Apply CZ in a Qmem.
input:
    position:(list of two. ex [0,1])position to apply CZ
'''
class QCZ(QuantumProgram):
    def __init__(self,position):
        self.position=position
        super().__init__()

    def program(self):
        #print("in QCZ ")
        self.apply(INSTR_CZ, qubit_indices=self.position, physical=True)
        yield self.run(parallel=False)
        
 

def logical_xor(str1, str2):
    return bool(str1) ^ bool(str2) 



def ProgramFail(info):
    print(info)
    print("Programme failed.")