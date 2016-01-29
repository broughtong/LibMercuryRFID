#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include "mercury/tm_reader.h"

TMR_Reader reader, *readerp;
TMR_ReadPlan plan;
TMR_ReadListenerBlock rlb;
TMR_ReadExceptionListenerBlock reb;
TMR_Region region;
TMR_Status status;
TMR_String model;

int16_t antennaMaxPower;
int16_t antennaMinPower;

typedef void (*py_callback)(char** tagID);
py_callback hPython;

void callback(TMR_Reader *reader, const TMR_TagReadData *t, void *cookie);
int run(py_callback python);
int closeRFID();
int checkError(TMR_Status status, const char* msg);
int getEnum(const char* string);

void callback(TMR_Reader *reader, const TMR_TagReadData *t, void *cookie)
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

	hPython(data);

	free(data);
}

void exceptionCallback(TMR_Reader *reader, TMR_Status error, void *cookie)
{
	fprintf(stderr, "Error:%s\n", TMR_strerr(reader, error));
}

int run(py_callback python)
{
	if(python == NULL)
	{
		printf("Error: No callback function provided\n");
		return -1;
	}
	if(*python == NULL)
	{
		printf("Error: No callback function provided\n");
		return -1;
	}

	hPython = python;

	readerp = &reader;
	if(checkError(TMR_create(readerp, "tmr:///dev/rfid"), "Creating reader"))
	{
		return -1;
	}
	if(checkError(TMR_connect(readerp), "Connecting to reader"))
	{
		return -1;
	}
	
	region = TMR_REGION_NONE;
	if(checkError(TMR_paramGet(readerp, TMR_PARAM_REGION_ID, &region), "Getting Saved Region"))
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

		if(checkError(TMR_paramGet(readerp, TMR_PARAM_REGION_SUPPORTEDREGIONS, &regions), "Getting List of Regions"))
		{
			return -1;
		}
		
		if(regions.len < 1)
		{
			printf("Reader doesn't support any regions\n");
			return -1;
		}

		region = regions.list[2];
		if(checkError(TMR_paramSet(readerp, TMR_PARAM_REGION_ID, &region), "Setting region"))
		{
			return -1;
		}
	}

	if(checkError(TMR_RP_init_simple(&plan, 0x0, NULL, TMR_TAG_PROTOCOL_GEN2, 1000), "Initialising read plan"))
	{
		return -1;
	}

	if(checkError(TMR_paramSet(readerp, TMR_PARAM_READ_PLAN, &plan), "Setting Read Plan"))
	{
		return -1;
	}

	rlb.listener = callback;
	rlb.cookie = NULL;

	reb.listener = exceptionCallback;
	reb.cookie = NULL;

	if(checkError(TMR_addReadListener(readerp, &rlb), "Adding read listener"))
	{
		return -1;
	}

	if(checkError(TMR_addReadExceptionListener(readerp, &reb), "Adding Exception Listener"))
	{
		return -1;
	}

	if(checkError(TMR_startReading(readerp), "Starting reader"))
	{
		return -1;
	}

	sleep(5);

	return 0;
}

int closeRFID()
{
	if(checkError(TMR_stopReading(readerp), "Stopping Reader"))
	{
		return -1;
	}

	TMR_destroy(readerp);

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
	int parameter = getEnum(parameterS);

	if(checkError(TMR_paramSet(readerp, parameter, value), "Setting External Parameter"))
	{
		return -1;
	}
	else
	{
		return 0;
	}
}
/*
void* getParameter(const char* parameterS
{
	int parameter = getEnum(parameterS);

	if(checkError(TMR_paramSet(readerp, parameter, 


}*/
