#include <iostream>
#include "rfid.h"

void myCallback(const char** message)
{
	//only uses message 0 and 1, more information is available, explained in docs
	std::cout << "Tag ID: " << message[0] << " RSSI: " << message[1] << std::endl;
}

int main(int argc, char *argv[])
{
	rfid::init();
	int reader = rfid::startReader("tmr:///dev/rfid", myCallback);

	std::cin.get();

	rfid::stopReader(reader);
	rfid::close();
	return 0;
}
