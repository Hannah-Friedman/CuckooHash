import BitHash
import pytest
import random


class CuckooHash(object):
    
    def __init__(self, size):
        self.__hashTableA = [None] * size
        self.__hashTableB = [None] * size
        self.__numKeys = 0
    
    
    def __str__(self):
        trackA = ""
        trackB = ""
        
        for i in range(len(self.__hashTableA)):
            if self.__hashTableA[i]:
                trackA += str( self.__hashTableA[i] ) + ", "

        for i in range(len(self.__hashTableB)):
            if self.__hashTableB[i]:
                trackB += str( self.__hashTableB[i] ) + ", "       
        return "[ " + trackA + " ] " + " [ " + trackB + " ]" 
    
    # return current number of keys in table   
    def __len__(self):
        return self.__numKeys
      
        
    # returns True if the key is in the table 
    def find(self, k):
        
        # hash the key
        cellA = BitHash.BitHash(k,1) % len(self.__hashTableA)
        cellB = BitHash.BitHash(k,2) % len(self.__hashTableB)
        
        # if the key exists in the table and matches the search key 
        if self.__hashTableA[cellA] and self.__hashTableA[cellA][0] == k:
            return self.__hashTableA[cellA][1]
        elif self.__hashTableB[cellB] and self.__hashTableB[cellB][0] == k:
            return self.__hashTableB[cellB][1]
        
        return False
    
    
    # removes the key/data pair from the table
    def delete(self, k):
        
        cellA = BitHash.BitHash(k,1) % len(self.__hashTableA)
        cellB = BitHash.BitHash(k,2) % len(self.__hashTableB)
        
        #if the key exists and can be found in the table, then remove it
        if  self.__hashTableA[cellA] and self.__hashTableA[cellA][0] == k:
            self.__hashTableA[cellA] = None
        
        elif self.__hashTableB[cellB] and self.__hashTableB[cellB][0] == k:
            self.__hashTableB[cellB] = None
        
        self.__numKeys -= 1
        
        
    # insert key/data if the key isn't already in the table
    # grow it if it's half full or the threshHold was met
    def insert(self, k, d, count=0):
        
        # if the key isn't already in the table
        if self.find(k):
            return False
        
        # if the tables are half full, grow them
        if self.__numKeys > ( len(self.__hashTableA) // 2 ):  
            self.__growHash() 
        
        x = self.__insert(k, d)
        
        # if the threshHold was met, grow the tables
        if x != True:
            return self.__growHash(x)
        elif x == True:
            count = 1
        
        self.__numKeys += count 
        
        return True    
            
    def __insert(self, k, d, tableA=None, tableB=None ): 
        
        # set the hashTables
        if tableA == None and tableB == None:
            tableA = self.__hashTableA
            tableB = self.__hashTableB
        
        # hash the key 
        cellA = BitHash.BitHash(k,1) % len(tableA)
        
        # store whatever was previosuly in the cell in a temp
        tempA = tableA[cellA] 
        tempB = None
        # and insert the key and data
        tableA[cellA] = (k,d)
        threshHold = 1
        
        
        # while every element has not been properly inserted and the threshHold 
        # has not been met...
        while (tempA or tempB) and threshHold < 50:
            
            # first try and insert into the hashTableB
            if threshHold % 2 == 1:
                
                cellB = BitHash.BitHash(tempA[0],2) % len(tableB)
                
                # store whatever was previosuly in the cell in a temp
                tempB = tableB[cellB]
                
                # and insert the key and data
                tableB[cellB] = tempA
                
                threshHold += 1
                tempA = None
            
            # then try and insert into hashTableA
            else:
                
                cellA = BitHash.BitHash(tempB[0],1) % len(tableA) 
                
                tempA = tableA[cellA]
                tableA[cellA] = tempB   
                
                threshHold += 1
                tempB = None
            
         # if the threshold was met, return the uninserted element
        if threshHold >= 50:
            if tempA:
                return tempA
            else:
                return tempB
            
        return True 
            
        
    # growHash resets the bitHash and grows the hash tables. It takes an
    # optionl paramter if insert returned an element because the threshold was met
    def __growHash(self, temp=None):
        
        BitHash.ResetBitHash()
        
        # create a new hash table twice the size
        tempA = [None] * len(self.__hashTableA) * 2
        tempB = [None] * len(self.__hashTableB) * 2
        
        listA = []
        take1 = True
        
        # for each element in hashTableA
        for cellA in range(len(self.__hashTableA)):
            
             # if the element in the cell is not none...
            if self.__hashTableA[cellA]:

               # insert the element into the new hash table
                y = self.__insert( self.__hashTableA[cellA][0], self.__hashTableA[cellA][1], tempA, tempB )
               
                # if the insert returned an element (because the threshHold was met), add it to listA
                if y != True: 
                    listA += [y]
        
        # do the same for hashTableB
        for cellB in range(len(self.__hashTableB)):
            
            if self.__hashTableB[cellB]:
                z = self.__insert( self.__hashTableB[cellB][0], self.__hashTableB[cellB][1], tempA, tempB)
                
                if z != True:
                    listA += [z]                
            
        # set the new hash tables
        self.__hashTableA = tempA
        self.__hashTableB = tempB
        
        # for each element in listA, reinsert it into the hash table 
        for i in range(len(listA)):
            t1 = listA[i]
            take1 = self.insert(t1[0], t1[1], 0)            
        
        # if an element was passed in, insert it
        if temp:
            x = self.insert(temp[0], temp[1], 0)
            
            # if the insert failed, all measures have been attempted, so return False
            if x != True or take1 != True:
                return False
            
        return True
       
       
       
       
       
# Pytests

def randomString(size):
    ans = ""
    for i in range(size):
        ans += ( chr(random.randint(0,25) + ord('A')) )
    return ans

    
# all inserts did not fail 
def test_simple():
    c = CuckooHash(1000)
    k = random.random()
    failed = False
    
    for i in range(1000):
        inserted = c.insert(randomString(9) ,randomString(9))
        
        if inserted == False:
            failed = True
        
    assert failed == False

# a key/data pair can't be inserted again
def test_noDoubles():
    c = CuckooHash(100)
    k = random.random()
    didNotInsert = True
    
    c.insert("double" , "insert")
    
    for i in range(100):
        inserted = c.insert("double" , "insert")
        
        if inserted == True:
            didNotInsert = False
        
    assert didNotInsert == True
        
        
# all inserts did not fail 
def test_overLoad():
    c = CuckooHash(100)
    k = random.random()
    failed = False
    
    for i in range(1000):
        inserted = c.insert(randomString(9) ,randomString(9))
        
        if inserted == False:
            failed = True
        
    assert failed == False
        

# all inserted keys can be found in the Cuckoo Hash
def test_noneLost():
    c = CuckooHash(1000)
    k = random.random()
    
    comp = []
    noneFound = False 
    
    for i in range(1000):
        r1 = randomString(9)
        r2 = randomString(9)
        c.insert( r1 , r2 )
        comp.append(r1)
    
    ans = []
    for j in range(len(comp)):
        if not c.find(comp[j]):
            ans.append(comp[j])
            noneFound = True
    
    assert noneFound == False


# all inserted keys can be found in the Cuckoo Hash
def test_noneLostOverLoad():
    c = CuckooHash(10)
    k = random.random()
    
    comp = []
    noneFound = False 
    
    for i in range(1000):
        r1 = randomString(9)
        r2 = randomString(9)
        c.insert( r1 , r2 )
        comp.append(r1)
    
    ans = []
    for j in range(len(comp)):
        if not c.find(comp[j]):
            ans.append(comp[j])
            noneFound = True
    
    assert noneFound == False
    
    
# keys that shouldn't be found are not wrongly found
def test_shouldNotFind():
    c = CuckooHash(1000)
    k = random.random()
    
    comp = []
    found = False 
    
    for i in range(1000):
        r1 = randomString(9)
        r2 = randomString(9)
        c.insert( r1 , r2 )
        comp.append(r1)
    
    for j in range(1000):
        if c.find(randomString(9)):
            found = True
    
    assert found == False


# delete doesn't delete what it should not and all keys can still be found
def test_shouldNotDelete():
    c = CuckooHash(100)
    k = random.random()
    deleted = False
    comp = []
    
    for i in range(1000):
        r1 = randomString(9)
        r2 = randomString(9)
        
        c.insert( r1 , r2 )
        comp.append(r1)
        
    for i in range(2000):
        c.delete(randomString(9))
    
    for i in range(1000):
        if not c.find(comp[i]):
            deleted = True
    
    assert deleted == False
    
    
# insert and delete elements and make sure none of the elements remain
def test_torture():
    c = CuckooHash(100)
    k = random.random()
    found = False
    comp = []
    
    for i in range(1000):
        r1 = randomString(9)
        r2 = randomString(9)
        
        c.insert( r1 , r2 )
        comp.append(r1)
        
    for i in range(1000):
        c.delete(comp[i])
    
    for i in range(1000):
        if c.find(comp[i]):
            found = True
    
    assert found == False


# insert and delete elements and make sure none of the elements remain
def test_superTorture():
    c = CuckooHash(10)
    k = random.random()
    found = False
    comp = []
    
    for i in range(10000):
        r1 = randomString(9)
        r2 = randomString(9)
        c.insert( r1 , r2 )
        comp.append(r1)
        c.delete(comp[i])
    
    for i in range(10000):
        if c.find(comp[i]):
            found = True
    
    assert found == False
    

pytest.main(["-v", "-s", "CuckooHash.py"])