#include <iostream>

extern "C"
{
	int startReader(const char* deviceURI, void (*callback)(const char** message));
	int stopReader(int readerID);
	int closeRFID();
}

void myCallback(const char** message)
{
	std::cout << "message received" << std::endl;
}

int main(int argc, char *argv[])
{
	int readerID = startReader("tmr:///dev/ttyUSB0", &myCallback);

	std::cin.get();

	stopReader(readerID);
	closeRFID();

	return 0;
}
