import numpy as np
import time
import random
import array

from random import SystemRandom
from operator import itemgetter

cimport cython
cimport numpy as np

from libc.stdlib cimport qsort
from cpython cimport array
from libc.stdlib cimport malloc, free

DTYPE = np.int
ctypedef np.int_t DTYPE_t

cdef extern from "stdlib.h":
    ctypedef void const_void "const void"
    void qsort(void *base, int nmemb, int size,
                int(*compar)(const_void *, const_void *)) nogil

cdef int mycmp(const_void * pa, const_void * pb):
    cdef int a = (<int *>pa)[0]
    cdef int b = (<int *>pb)[0]
    if a < b:
        return 1
    elif a > b:
        return -1
    else:
        return 0
    
cdef int getStraight(int *cards, int count):
    cdef int high, low
    if count >= 5:
        if cards[0] == 12:
            cards[count] = -1
            count += 1
        for i in range(count - 4):
            high = cards[i]
            low = cards[i + 4]
            if high - low == 4:
                return high
    return 0

cdef get_best_hand_v5(cards): # For testing purposes
    sortedCards = sorted(cards, key=itemgetter(0), reverse=True) + [(-10, -10)] # Added termination card
    cardsBySuit = [array.array('i',[]) for _ in range(4)]
    rankCounts = [array.array('i', []) for _ in range(4)] # Represents quads, trips, pairs and highcards
    cardsByRank = array.array('i', [])
    
    previousRank = -1
    rankCount = 0
    for r, s in sortedCards:
        if previousRank == -1:
            previousRank = r
            cardsByRank.append(r)
        elif r != previousRank:
            if rankCount == 3:
                kicker = cardsByRank[0] if cardsByRank[0] != previousRank else r
                return [7, previousRank, kicker]
            elif rankCount == 2 and len(rankCounts[2]) == 1: # Add second trips as pair
                rankCounts[1].append(previousRank)
            elif rankCount == 1 and len(rankCounts[1]) == 2: # Add third pair as high card
                rankCounts[0].append(previousRank)
            else:
                rankCounts[rankCount].append(previousRank)
            if r != -10:
                cardsByRank.append(r)
                previousRank = r
                rankCount = 0
        else:
            rankCount += 1
        if r != -10:
            cardsBySuit[s].append(r)
        
    possibleFlush = max(cardsBySuit, key=len)
    if len(possibleFlush) >= 5:
        if possibleFlush[0] == 12: # Add ace as the lowest card as well
            possibleFlush.append(-1)
        for h, l in ((possibleFlush[i], possibleFlush[i + 4]) for i in range(len(possibleFlush) - 4)):
            if h - l == 4:
                return [8, h]
            
    if len(rankCounts[2]) == 1 and len(rankCounts[1]) >= 1:
        return [6, rankCounts[2][0], rankCounts[1][0]]
    if len(possibleFlush) >= 5:
        return [5, possibleFlush[0], possibleFlush[1], possibleFlush[2], possibleFlush[3], possibleFlush[4]]
    
    if len(cardsByRank) >= 5:
        if cardsByRank[0] == 12: # Add ace as the lowest card as well
            cardsByRank.append(-1)
        for h, l in ((cardsByRank[i], cardsByRank[i + 4]) for i in range(len(cardsByRank) - 4)):
            if h - l == 4:
                return [4, h]
            
    if len(rankCounts[2]) == 1:
        return [3, rankCounts[2][0], rankCounts[0][0], rankCounts[0][1]]
    if len(rankCounts[1]) > 0:
        if len(rankCounts[1]) == 2:
            return [2, rankCounts[1][0], rankCounts[1][1], rankCounts[0][0]]
        else:
            return [1, rankCounts[1][0], rankCounts[0][0], rankCounts[0][1], rankCounts[0][2]]
        
    return [0, cardsByRank[0], cardsByRank[1], cardsByRank[2], cardsByRank[3], cardsByRank[4]]


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def fast_eval(cards):
    cdef int numCards = len(cards)
    cdef int i
        
    cdef int *sortedCards = <int *>malloc(numCards * sizeof(int) * 2)
    cdef int **cardsBySuit = <int **>malloc(4 * sizeof(int *))
    cdef int *cardsBySuit_c = <int *>malloc(4 * sizeof(int))
    cdef int **rankCounts = <int **>malloc(4 * sizeof(int *))
    cdef int *rankCounts_c = <int *>malloc(4 * sizeof(int))
    cdef int *cardsByRank = <int *>malloc((numCards + 1) * sizeof(int)) # Extra slot for possible ace addition for straight check
    cdef int cardsByRank_c = 0
    
    for i in range(4):
        cardsBySuit[i] = <int *>malloc((numCards + 1) * sizeof(int)) # Extra slot for possible ace addition for straight check
        rankCounts[i] = <int *>malloc(numCards * sizeof(int))
        cardsBySuit_c[i] = 0
        rankCounts_c[i] = 0
    
    for i in range(numCards):
        sortedCards[2 * i] = cards[i][0]
        sortedCards[2 * i + 1] = cards[i][1]
        
    cdef int rankCount = 0
    cdef int rank, suit, previousRank
    cdef int flushIndex, possibleStraight
    cdef int *temp
    
    try:
        qsort(sortedCards, numCards, 2 * sizeof(int), mycmp)
           
        for i in range(numCards + 1):
            if i != numCards:
                rank = sortedCards[i * 2]
                suit = sortedCards[i * 2 + 1]
            if i == 0:
                previousRank = rank
                cardsByRank[cardsByRank_c] = rank
                cardsByRank_c += 1
            elif i == numCards or rank != previousRank:
                if rankCount == 3:
                    kicker = cardsByRank[0] if cardsByRank[0] != previousRank else rank
                    return (7, previousRank, kicker)
                elif rankCount == 2 and rankCounts_c[2] == 1:
                    rankCounts[1][rankCounts_c[1]] = previousRank
                    rankCounts_c[1] += 1
                elif rankCount == 1 and rankCounts_c[1] == 2:
                    rankCounts[0][rankCounts_c[0]] = previousRank
                    rankCounts_c[0] += 1
                else:
                    rankCounts[rankCount][rankCounts_c[rankCount]] = previousRank
                    rankCounts_c[rankCount] += 1
                if i != numCards:
                    cardsByRank[cardsByRank_c] = rank
                    cardsByRank_c += 1
                    previousRank = rank
                    rankCount = 0
            else:
                rankCount += 1
            if i != numCards:
                cardsBySuit[suit][cardsBySuit_c[suit]] = rank
                cardsBySuit_c[suit] += 1
        
        for i in range(4):
            if i == 0:
                flushIndex = 0
            else:
                if cardsBySuit_c[i] > cardsBySuit_c[flushIndex]:
                    flushIndex = i
        if cardsBySuit_c[flushIndex] >= 5:
            possibleStraight = getStraight(cardsBySuit[flushIndex], cardsBySuit_c[flushIndex])  
            if possibleStraight != 0:
                return (8, possibleStraight)
                
        if rankCounts_c[2] == 1 and rankCounts_c[1] >= 1:
            return (6, rankCounts[2][0], rankCounts[1][0])
        
        if cardsBySuit_c[flushIndex] >= 5:
            temp = cardsBySuit[flushIndex]
            return (5, temp[0], temp[1], temp[2], temp[3], temp[4])
        
        if cardsByRank_c >= 5:
            possibleStraight = getStraight(cardsByRank, cardsByRank_c)
            if possibleStraight != 0:
                return (4, possibleStraight) 
           
        if rankCounts_c[2] == 1:
            return (3, rankCounts[2][0], rankCounts[0][0], rankCounts[0][1])
        if rankCounts_c[1] > 0:
            if rankCounts_c[1] == 2:
                return (2, rankCounts[1][0], rankCounts[1][1], rankCounts[0][0])
            else:
                return (1, rankCounts[1][0], rankCounts[0][0], rankCounts[0][1], rankCounts[0][2])
        
        temp = cardsByRank
        return (0, temp[0], temp[1], temp[2], temp[3], temp[4])
    
    finally:
        for i in range(4):
            free(cardsBySuit[i])
            free(rankCounts[i])
            
        free(sortedCards)
        free(cardsBySuit)
        free(cardsBySuit_c)
        free(rankCounts)
        free(rankCounts_c)
        free(cardsByRank)

def start(errorCheck = False):
    cdef int i = 0
    cdef int errors = 0
    cdef int iters = 1000000
        
    cards = [[(i % 13, int(i / 13)) for i in random.sample(range(52), random.randint(5, 7))] for _ in range(iters)]
    
    cdef tuple str1
    if errorCheck:
        for i in range(iters):       
            str1 = fast_eval(cards[i])
            str2 = get_best_hand_v5(cards[i])
            if len(str1) != len(str2):
                errors += 1
            else:
                for d1, d2 in zip(str1, str2):
                    if d1 != d2:
                        errors += 1
                        
            if i % (iters / 10) == 0:
                print("Cards: " + repr(sorted(cards[i], key=itemgetter(0), reverse=True)))
                print("Str1:  " + repr(str1))
                print("Str2:  " + repr(str2))
                print("")
    
    start = time.time()
    for i in range(iters):
        str1 = fast_eval(cards[i])
             
    end = time.time()
    print(repr(iters / (end - start)))
    print("Errors: " + repr(errors))
    
            