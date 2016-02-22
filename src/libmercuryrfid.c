#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include "tm_reader.h"

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

typedef void (*PythonCallback)(char** message);
PythonCallback pythonCallback;

void callback(TMR_Reader *reader, const TMR_TagReadData *t, void *cookie);
int run(const char* deviceURI, PythonCallback python);
int closeRFID();
int checkError(TMR_Status status, const char* msg);
int getEnum(const char* string);

void tagCallback(TMR_Reader *readerr, const TMR_TagReadData *t, void *cookie)
{
	char** data = malloc(sizeof(char*) * 6);

	char tagID[128];
	char tagRSSI[20];
	char tagPhase[20];
	char tagFrequency[20];
	char tagTimeStampHigh[20];
	char tagTimeStampLow[20];
	
	TMR_bytesToHex(t->tag.epc, t->tag.epcByteCount, tagID);
	data[0] = tagID;

	sprintf(tagRSSI, "%d", t->rssi);	
	data[1] = tagRSSI;

	sprintf(tagPhase, "%i", t->phase);	
	data[2] = tagPhase;

	sprintf(tagFrequency, "%i", t->frequency);	
	data[3] = tagFrequency;

	sprintf(tagTimeStampHigh, "%i", t->timestampHigh);	
	data[4] = tagTimeStampHigh;

	sprintf(tagTimeStampLow, "%ui", t->timestampLow);	
	data[5] = tagTimeStampLow;

	pythonCallback(data);

	free(data);
}

void exceptionCallback(TMR_Reader *reader, TMR_Status error, void *cookie)
{
	fprintf(stderr, "Error:%s\n", TMR_strerr(reader, error));
}

int startReader(const char* deviceURI, PythonCallback callbackHandle)
{
	if(callbackHandle == NULL)
	{
		printf("Error: No callback function provided\n");
		return -1;
	}

	pythonCallback = callbackHandle;

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

	if(region == TMR_REGION_NONE)
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

		*(region[readerCount]) = regions.list[2];
		if(checkError(TMR_paramSet(readers[readerCount], TMR_PARAM_REGION_ID, &region), "Setting region"))
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

int closeRFID()
{
	/*if(checkError(TMR_stopReading(readerp), "Stopping Reader"))
	{
		return -1;
	}

	TMR_destroy(readerp);*/

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

int setParameter(const char* parameterS, const char* value)
{
	/*int parameter = getEnum(parameterS);

	if(checkError(TMR_paramSet(readerp, parameter, value), "Setting External Parameter"))
	{
		return -1;
	}
	else
	{
		return 0;
	}*/
	return 0;
}
/*
void* getParameter(const char* parameterS
{
	int parameter = getEnum(parameterS);

	if(checkError(TMR_paramSet(readerp, parameter, 


}*/
