#include "rfid.h"

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
