#include <iostream>
#include "rfid.h"

void myCallback(const char* message)
{
	printf("message received");
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
