#include <iostream>
#include "rfid.h"

void myCallback(char* message)
{
	std::cout << "Tag ID: " << message[0] << " RSSI: " << message[1] << std::endl;
}

int main(int argc, char *argv[])
{
	rfid::init();
	rfid::ReaderID readerID = rfid::startReader("tmr:///dev/rfid", myCallback);

	std::cin.get();

	rfid::stopReader(readerID);
	rfid::close();
	return 0;
}
