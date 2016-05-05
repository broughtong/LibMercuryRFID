#include "rfid.h"

extern "C"
{
	int startReader(const char* deviceURI, void (*callback)(const char** message));
	int stopReader(int readerID);
	int closeRFID();
}

void init()
{
	//start comms etc
}

int startReader(const char* deviceURI, void* callbackFunction)
{
	int readerID = startReader(deviceURI, callbackFunction);

	return readerID;
}

void stopReaderF(int readerID)
{
	int a = stopReader(readerID);
}

void close()
{
	closeRFID();
}
