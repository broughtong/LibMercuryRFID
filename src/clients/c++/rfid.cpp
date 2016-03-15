#include "rfid.h"

extern "C"
{
	int startReader(const char* deviceURI, void (*callback)(const char** message));
	int stopReader(int readerID);
	int closeRFID();
}

void rfid::init()
{
	//start comms etc
}

int rfid::startReader(const char* deviceURI, void* callbackFunction)
{
	int readerID = startReader(deviceURI, callbackFunction);

	return readerID;
}

void rfid::stopReader(int readerID)
{
	stopReader(readerID);
}

void rfid::close()
{
	closeRFID();
}
