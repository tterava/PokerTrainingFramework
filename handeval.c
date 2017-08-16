#include <Python.h>
#include <stdbool.h>
#include "pcg/pcg_basic.h"

static bool b_seeded = false;

static inline void fillTuple(PyObject * target, int * values, int count)
{
	for (int i = 0; i < count; i++)
	{
		PyObject *n = PyTuple_New(2);
		PyTuple_SET_ITEM(n, 0, PyLong_FromLong(values[i] % 13));
		PyTuple_SET_ITEM(n, 1, PyLong_FromLong((int) values[i] / 13));
		PyTuple_SET_ITEM(target, i, n);
	}
}

static PyObject *formatEval(int values[], int count)
{
	PyObject *ret = PyTuple_New(count);
	for (int i = 0; i < count; i++)
		PyTuple_SET_ITEM(ret, i, PyLong_FromLong(values[i]));
	return ret;
}

void insertionSort(int arr[], int n)
{
	int i, key, addon, j;
	for (i = 2; i < n * 2; i += 2)
	{
		key = arr[i];
		addon = arr[i + 1];
		j = i-2;

		while (j >= 0 && arr[j] < key)
		{
			memcpy(&arr[j+2], &arr[j], sizeof(int) * 2);
			j = j-2;
		}
		arr[j+2] = key;
		arr[j+3] = addon;
	}
}

static int findStraight(int *cards, int count)
{
    int high, low;
    if (count >= 5)
    {
        if (cards[0] == 12)
        {
            cards[count] = -1;
            count += 1;
        }
        for (int i = 0; i < count - 4; i++)
        {
            high = cards[i];
            low = cards[i + 4];
            if (high - low == 4)
                return high;
        }
    }
    return 0;
}

static PyObject *evaluate(int values[], int numCards)
{
	int sortedCards[numCards * 2];

	int cardsBySuit[4][numCards + 1]; // Extra slot for possible ace addition for straight check
	int cardsBySuit_c[4] = {0, 0, 0, 0};

	int rankCounts[4][numCards];
	int rankCounts_c[4] = {0, 0, 0, 0};

	int cardsByRank[numCards + 1]; // Extra slot for possible ace addition for straight check
	int cardsByRank_c = 0;

	memcpy(sortedCards, values, numCards * 2 * sizeof(int));
	insertionSort(sortedCards, numCards);

	int rankCount = 0;
	int rank, suit, previousRank, kicker,
		flushIndex, straight, *temp;

	for(int i = 0; i <= numCards; i++)
	{
		if (i != numCards)
		{
			rank = sortedCards[i * 2];
			suit = sortedCards[i * 2 + 1];

			cardsBySuit[suit][cardsBySuit_c[suit]] = rank;
			cardsBySuit_c[suit] += 1;
		}
		if (i == 0)
		{
			previousRank = rank;
			cardsByRank[cardsByRank_c] = rank;
			cardsByRank_c += 1;
		}
		else if (i == numCards || rank != previousRank)
		{
			if (rankCount == 3)
			{
				kicker = cardsByRank[0] != previousRank ? cardsByRank[0] : rank;
				return formatEval((int []) {7, previousRank, kicker}, 3);
			}
			else if (rankCount == 2 && rankCounts_c[2] == 1)
			{
				rankCounts[1][rankCounts_c[1]] = previousRank;
				rankCounts_c[1] += 1;
			}
			else if (rankCount == 1 && rankCounts_c[1] == 2)
			{
				rankCounts[0][rankCounts_c[0]] = previousRank;
				rankCounts_c[0] += 1;
			}
			else
			{
				rankCounts[rankCount][rankCounts_c[rankCount]] = previousRank;
				rankCounts_c[rankCount] += 1;
			}
			if (i != numCards)
			{
				cardsByRank[cardsByRank_c] = rank;
				cardsByRank_c += 1;
				previousRank = rank;
				rankCount = 0;
			}
		}
		else
			rankCount += 1;
	}

	for (int i = 0; i < 4; i++)
	{
		if (i == 0)
			flushIndex = 0;
		else if (cardsBySuit_c[i] > cardsBySuit_c[flushIndex])
			flushIndex = i;
	}

	if (cardsBySuit_c[flushIndex] >= 5)
	{
		straight = findStraight(cardsBySuit[flushIndex], cardsBySuit_c[flushIndex]);
		if (straight)
			return formatEval((int []) {8, straight}, 2);
	}

	if (rankCounts_c[2] == 1 && rankCounts_c[1] >= 1)
		return formatEval((int []) {6, rankCounts[2][0], rankCounts[1][0]}, 3);

	if (cardsBySuit_c[flushIndex] >= 5)
	{
		temp = cardsBySuit[flushIndex];
		return formatEval((int []) {5, temp[0], temp[1], temp[2], temp[3], temp[4]}, 6);
	}

	if (cardsByRank_c >= 5)
	{
		straight = findStraight(cardsByRank, cardsByRank_c);
		if (straight)
			return formatEval((int []) {4, straight}, 2);
	}

	if (rankCounts_c[2] == 1)
		return formatEval((int []) {3, rankCounts[2][0], rankCounts[0][0], rankCounts[0][1]}, 4);

	if (rankCounts_c[1] > 0)
	{
		if (rankCounts_c[1] == 2)
			return formatEval((int []) {2, rankCounts[1][0], rankCounts[1][1], rankCounts[0][0]}, 4);
		else
			return formatEval((int []) {1, rankCounts[1][0], rankCounts[0][0], rankCounts[0][1], rankCounts[0][2]}, 5);
	}

	temp = cardsByRank;
	return formatEval((int []) {0, temp[0], temp[1], temp[2], temp[3], temp[4]}, 6);
}

static PyObject *evalCards(PyObject *self, PyObject *args)
{
	PyObject *cardTuples;
	int expectedNum;
	if (!PyArg_ParseTuple(args, "Oi", &cardTuples, &expectedNum))
		return NULL;

	int numCards = PyList_GET_SIZE(cardTuples);
	if (numCards < 5 || numCards > 7 || expectedNum > numCards || expectedNum < 5)
	{
		return NULL;
	}

	numCards = expectedNum;
	int values[numCards * 2];
	for(int i = 0; i < numCards; i++)
	{
		PyObject *card;
		if (PyList_Check(cardTuples))
			card = PyList_GET_ITEM(cardTuples, i);
		else if (PyTuple_Check(cardTuples))
			card = PyTuple_GET_ITEM(cardTuples, i);
		else
			return NULL;

		values[i*2] = PyLong_AsLong(PyTuple_GET_ITEM(card, 0));
		values[i*2 + 1] = PyLong_AsLong(PyTuple_GET_ITEM(card, 1));
	}

	return evaluate(values, numCards);
}

static PyObject *constructHand()
{
	if (!b_seeded)
	{
		pcg32_srandom(time(NULL) ^ (intptr_t)&printf, (intptr_t)&b_seeded);
		b_seeded = true;
	}

	int sample[9];
	int space[52];
	for (int i = 0; i < 52; i++)
		space[i] = 0;

	int counter = 0;
	while (counter < 9)
	{
		int ran = pcg32_boundedrand(52);
		if (!space[ran])
		{
			space[ran] = 1;
			sample[counter] = ran;
			counter++;
		}
	}

	PyObject *top = PyTuple_New(3);

	PyObject *p1 = PyTuple_New(2);
	PyObject *p2 = PyTuple_New(2);
	PyObject *board = PyTuple_New(5);

	fillTuple(p1, &sample[0], 2);
	fillTuple(p2, &sample[2], 2);
	fillTuple(board, &sample[4], 5);

	PyTuple_SET_ITEM(top, 0, p1);
	PyTuple_SET_ITEM(top, 1, p2);
	PyTuple_SET_ITEM(top, 2, board);

	return top;
}

static PyObject *boundedRand(PyObject *self, PyObject *args)
{
	int bound;
	if (!PyArg_ParseTuple(args, "i", &bound))
		return NULL;

	if (!b_seeded)
	{
		pcg32_srandom(time(NULL) ^ (intptr_t)&printf, (intptr_t)&b_seeded);
		b_seeded = true;
	}

	return PyLong_FromLong(pcg32_boundedrand(bound));
}

static PyMethodDef EvalMethods[] = {
	{"gethand", constructHand, METH_NOARGS,
	 "Generate p1, p2 and board cards"},
	{"fasteval", evalCards, METH_VARARGS,
	 "Evaluates 5-7 card hand."},
	{"pcg_brand", boundedRand, METH_VARARGS,
	 "Fast bounded random number"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef handeval = {
   PyModuleDef_HEAD_INIT,
   "Hand evaluator",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   EvalMethods
};

PyMODINIT_FUNC
PyInit_handeval(void)
{
    return PyModule_Create(&handeval);
}



