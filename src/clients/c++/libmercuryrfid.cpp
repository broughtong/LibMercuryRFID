//compile with g++ -fPIC -shared libmercuryrfid.cpp -o libmercuryrfid-c.so.1
#include "rfid.h"

void rfid::init(rfid::ForeignCallback callbackHandle)
{
	rfid::RFIDinit(callbackHandle);
}

rfid::ReaderID rfid::startReader(const char* deviceURI)
{
	rfid::RFIDstartReader(const char* deviceURI);
}

void rfid::stopReader(rfid::ReaderID readerID);
{
	rfid::RFIDstopReader(rfid::ReaderID readerID);
}

void rfid::close();
{
	rfid::RFIDclose();
}
