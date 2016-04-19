#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <inttypes.h>

#include "tm_reader.h"
#include "queue.h"

int readerCount = 0;
int uniqueReaderInstance = 0;
TMR_Reader ** readers = NULL;
TMR_ReadPlan** plan = NULL;
TMR_ReadListenerBlock** rlb = NULL;
TMR_ReadExceptionListenerBlock** reb = NULL;
TMR_Region** region = NULL;
TMR_Status** status = NULL;
TMR_String** model = NULL;

int16_t antennaMaxPower;
int16_t antennaMinPower;

typedef void (*ForeignCallback)(char* message);
ForeignCallback foreignCallback;

void callback(TMR_Reader *reader, const TMR_TagReadData *t, void *cookie);
int checkError(TMR_Status status, const char* msg);
int getEnum(const char* string);

typedef int ReaderID;
void* communicatorThreadFunction();
Queue* communicatorQueue;

int RFIDinit(ForeignCallback callbackHandle)
{
	if(callbackHandle == NULL)
	{
		printf("Error: No callback function provided\n");
		return -1;
	}

	foreignCallback = callbackHandle;

	communicatorQueue = createQueue();
	pthread_t communicatorThread;
	pthread_create(&communicatorThread, NULL, communicatorThreadFunction, (void*) communicatorQueue);

	return 0;
}

int RFIDclose()
{
	Enqueue(communicatorQueue, "exit");

	int i;

	for(i = 0; i < readerCount; i++)
	{
		TMR_stopReading(readers[i]);
		TMR_destroy(readers[i]);
		free(readers[i]);
		free(plan[i]);
		free(rlb[i]);
		free(reb[i]);
		free(region[i]);
		free(status[i]);
		free(model[i]);
	}

	free(readers);
	free(plan);
	free(rlb);
	free(reb);
	free(region);
	free(status);
	free(model);

	return 0;
}

void* communicatorThreadFunction(void* messageQueue)
{
	int isThreadRunning = 1;

	while(isThreadRunning)
	{
		char* message = Dequeue(messageQueue);

		if(message != NULL)
		{
			//printf("message receivde\n");
			if(strcmp(message, "exit") == 0)
			{
				isThreadRunning = 0;
			}
			else
			{
				//printf("thread saw a tag!!: %s\n", message);
				foreignCallback(message);
				//printf("thread message send!\n");
			}
		}
		else
		{
			int milliseconds = 5;
			usleep(1000*milliseconds);
		}
	}
	printf("closing\n");
	return NULL;
}

void tagCallback(TMR_Reader *readerr, const TMR_TagReadData *t, void *cookie)
{
	int i;
	int readerLocation;

	for(i = 0; i < uniqueReaderInstance; i++)
	{
		if(readers[i] == readerr)
		{
			readerLocation = i;
		}
	}

	char tagID[128];
	TMR_bytesToHex(t->tag.epc, t->tag.epcByteCount, tagID);

	char msg[256];
	sprintf(msg, "%i:%s:%d:%i:%i:%u:%u", readerLocation, tagID, t->rssi, t->phase, t->frequency, t->timestampHigh, t->timestampLow);

	uint64_t timestamp = ((uint64_t) t->timestampHigh<< 32 ) | t->timestampLow;

	Enqueue(communicatorQueue, msg);
}

void exceptionCallback(TMR_Reader *reader, TMR_Status error, void *cookie)
{
	fprintf(stderr, "Error:%s\n", TMR_strerr(reader, error));
}

int startReader(const char* deviceURI)
{
	readers = realloc(readers, (readerCount + 1) * sizeof(TMR_Reader*));
	TMR_Reader* pr = malloc(sizeof(TMR_Reader));
	readers[readerCount] = pr;

	plan = realloc(plan, (readerCount + 1) * sizeof(TMR_ReadPlan*));
	TMR_ReadPlan* prp = malloc(sizeof(TMR_ReadPlan));
	plan[readerCount] = prp;

	rlb = realloc(rlb, (readerCount + 1) * sizeof(TMR_ReadListenerBlock*));
	TMR_ReadListenerBlock* prlb = malloc(sizeof(TMR_ReadListenerBlock));
	rlb[readerCount] = prlb;

	reb = realloc(reb, (readerCount + 1) * sizeof(TMR_ReadExceptionListenerBlock*));
	TMR_ReadExceptionListenerBlock* preb = malloc(sizeof(TMR_ReadExceptionListenerBlock));
	reb[readerCount] = preb;

	region = realloc(region, (readerCount + 1) * sizeof(TMR_Region*));
	TMR_Region* preg = malloc(sizeof(TMR_Region));
	region[readerCount] = preg;

	status = realloc(status, (readerCount + 1) * sizeof(TMR_Status*));
	TMR_Status* pstat = malloc(sizeof(TMR_Status));
	status[readerCount] = pstat;

	model = realloc(model, (readerCount + 1) * sizeof(TMR_String*));
	TMR_String* pstr = malloc(sizeof(TMR_String));
	model[readerCount] = pstr;

	if(checkError(TMR_create(readers[readerCount], deviceURI), "Creating reader"))
	{
		return -1;
	}
	if(checkError(TMR_connect(readers[readerCount]), "Connecting to reader"))
	{
		return -1;
	}

	*(region[readerCount]) = TMR_REGION_NONE;
	if(checkError(TMR_paramGet(readers[readerCount], TMR_PARAM_REGION_ID, region[readerCount]), "Getting Saved Region"))
	{
		return -1;
	}

	if(*(region[readerCount]) == TMR_REGION_NONE)
	{
		printf("No saved regions\n");

		TMR_RegionList regions;
		TMR_Region _regionStore[32];
		regions.list = _regionStore;
		regions.max = sizeof(_regionStore)/sizeof(_regionStore[0]);
		regions.len = 0;

		if(checkError(TMR_paramGet(readers[readerCount], TMR_PARAM_REGION_SUPPORTEDREGIONS, &regions), "Getting List of Regions"))
		{
			return -1;
		}

		if(regions.len < 1)
		{
			printf("Reader doesn't support any regions\n");
			return -1;
		}

		*(region[readerCount]) = regions.list[0];
		if(checkError(TMR_paramSet(readers[readerCount], TMR_PARAM_REGION_ID, &*(region[readerCount])), "Setting region"))
		{
			return -1;
		}
	}

	if(checkError(TMR_RP_init_simple(plan[readerCount], 0x0, NULL, TMR_TAG_PROTOCOL_GEN2, 1000), "Initialising read plan"))
	{
		return -1;
	}

	if(checkError(TMR_paramSet(readers[readerCount], TMR_PARAM_READ_PLAN, plan[readerCount]), "Setting Read Plan"))
	{
		return -1;
	}

	rlb[readerCount]->listener = tagCallback;
	rlb[readerCount]->cookie = NULL;

	reb[readerCount]->listener = exceptionCallback;
	reb[readerCount]->cookie = NULL;

	if(checkError(TMR_addReadListener(readers[readerCount], rlb[readerCount]), "Adding read listener"))
	{
		return -1;
	}

	if(checkError(TMR_addReadExceptionListener(readers[readerCount], reb[readerCount]), "Adding Exception Listener"))
	{
		return -1;
	}

	if(checkError(TMR_startReading(readers[readerCount]), "Starting reader"))
	{
		return -1;
	}

	uniqueReaderInstance++;

	return (uniqueReaderInstance - 1);
}

int stopReader()
{
	return 0;
}

int checkError(TMR_Status status, const char* msg)
{
	if(status == TMR_SUCCESS)
	{
		printf("%s: Ok\n", msg);
		return 0;
	}
	printf("%s: Failed\n", msg);
	return 1;
}

void getPower(int readerID)
{
	int16_t max, min;
	int32_t current;

	checkError(TMR_stopReading(readers[readerID]), "Stopping Reader for power reading");

	TMR_paramGet(readers[readerID], TMR_PARAM_RADIO_POWERMAX , &max);
	TMR_paramGet(readers[readerID], TMR_PARAM_RADIO_POWERMIN , &min);
	TMR_paramGet(readers[readerID], TMR_PARAM_RADIO_READPOWER , &current);

	printf("Max transmission power is: %i\n", max);
	printf("Min transmission power is: %i\n", min);
	printf("Current transmission power is: %i\n", current);

	checkError(TMR_startReading(readers[readerID]), "Starting reader");
}

int setPower(int readerID, int value)
{
	printf("Setting read power\n");

	checkError(TMR_stopReading(readers[readerID]), "Stopping Reader for power reading");
	if(checkError(TMR_paramSet(readers[readerID], TMR_PARAM_RADIO_READPOWER, &value), "Setting Radio Power"))
	{
		return -1;
	}
	checkError(TMR_startReading(readers[readerID]), "Starting reader");
	return 0;
}

void getHopTime(int readerID)
{
	checkError(TMR_stopReading(readers[readerID]), "Stopping reader for hop time reading");

	uint32_t hoptimeval;

	TMR_paramGet(readers[readerID], TMR_PARAM_REGION_HOPTIME, &hoptimeval);
	//TMR_paramGet(readers[readerID], TMR_PARAM_REGION_HOPTABLE, &);

	printf("HOPTIME: %" PRIu32  "\n", hoptimeval);
	//printf("HOPTABLE: \n");

	checkError(TMR_startReading(readers[readerID]), "Starting Reader");

}

void setHopTime(int readerID, int value)
{
	uint32_t hoptime = (uint32_t) value;

	printf("New hoptime is: %" PRIu32 "\n", hoptime);

	checkError(TMR_stopReading(readers[readerID]), "Stopping reader for hop time reading");

	checkError(TMR_paramSet(readers[readerID], TMR_PARAM_REGION_HOPTIME, &hoptime), "Setting hoptime");

	checkError(TMR_startReading(readers[readerID]), "Starting reader");

}

int setParameter(const char* parameterS, const char* value)
{
	return 0;
	/*int parameter = getEnum(parameterS);

	if(checkError(TMR_paramSet(readerp, parameter, value), "Setting External Parameter"))
	{
		return -1;
	}
	else
	{
		return 0;
	}*/
}

/*
void* getParameter(const char* parameterS
{
	int parameter = getEnum(parameterS);

	if(checkError(TMR_paramSet(readerp, parameter,


}*/
