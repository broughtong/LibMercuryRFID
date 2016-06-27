#include <pthread.h>

struct QueueElement
{
	char* data;
	struct QueueElement* nextElement;
};

typedef struct QueueStructure
{
	struct QueueElement* firstElement;
	struct QueueElement* lastElement;

	pthread_mutex_t queueLock;
}Queue;

Queue* createQueue();

void Enqueue(struct QueueStructure *q, char* data);

char* Dequeue(struct QueueStructure *q);

