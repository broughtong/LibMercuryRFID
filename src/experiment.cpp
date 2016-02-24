#include <iostream>
#include "rfid.h"

void myCallback(const char** message)
{
	std::cout << "Tag ID: " << message[0] << " RSSI: " << message[1] << std::endl;
}

int main(int argc, char *argv[])
{
	rfid::ReaderID readerID = rfid::startReader("tmr:///dev/ttyUSB0", &myCallback);

	std::cin.get();

	rfid::stopReader(readerID);
	rfid::closeRFID();

	return 0;
}
