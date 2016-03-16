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
	
	pthread_mutex_t EnqueueLock;
	pthread_mutex_t DequeueLock;
}Queue;

Queue* createQueue();

void Enqueue(struct QueueStructure *q, char* data);

int Dequeue(struct QueueStructure *q);

