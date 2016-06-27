#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include "queue.h"

Queue* createQueue()
{
	Queue *q;
	q = (Queue*)malloc(sizeof(Queue));
	if(!q)
	{
		return NULL;
	}

	if(pthread_mutex_init(&q->queueLock, NULL) != 0)
	{
		free(q);
		return NULL;
	}

	q->firstElement = NULL;
	q->lastElement = NULL;

	return q;
}

void Enqueue(struct QueueStructure *q, char* data)
{
	pthread_mutex_lock(&q->queueLock);

	if(q->firstElement == NULL)
	{
		struct QueueElement* newElement = malloc(sizeof(struct QueueElement));

		newElement->nextElement = NULL;
		newElement->data = data;

		q->firstElement = newElement;
		q->lastElement = newElement;
	}
	else
	{
		struct QueueElement* newElement = malloc(sizeof(struct QueueElement));

		newElement->nextElement = NULL;
		newElement->data = data;

		q->lastElement->nextElement = newElement;
		q->lastElement = newElement;
	}

	pthread_mutex_unlock(&q->queueLock);
}

char* Dequeue(struct QueueStructure *q)
{
	pthread_mutex_lock(&q->queueLock);

	if(q->firstElement == NULL)
	{
		pthread_mutex_unlock(&q->queueLock);
		return NULL;
	}

	char* data = q->firstElement->data;

	struct QueueElement* oldNext = q->firstElement;
	struct QueueElement* newNext = q->firstElement->nextElement;

	free(oldNext);

	q->firstElement = newNext;

	pthread_mutex_unlock(&q->queueLock);

	return data;
}

void deleteQueue(struct QueueStructure *q)
{
	//traverse q deleteing elements
	free(q);
	pthread_mutex_destroy(&q->queueLock);
}
