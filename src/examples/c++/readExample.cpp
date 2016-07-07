//compile with a g++ readExample.cpp -lmercuryrfid
//then a sudo ./a.out

#include <iostream>
//#include "rfid.h"

namespace rfid
{
	typedef int ReaderID;
	typedef void (*ForeignCallback)(const char* message);

	//void init();
	//ReaderID startReader(const char* deviceURI, ForeignCallback callbackHandle);
	//void stopReader(ReaderID readerID);
	//void close();

	extern "C"
	{
		int RFIDinit(ForeignCallback callbackHandle);
		int RFIDclose();
		int RFIDstartReader(const char* deviceURI);
		int RFIDstopReader(ReaderID readerID);
	}
}

void myCallback(const char* message)
{
	std::cout << message << std::endl;
}

int main(int argc, char *argv[])
{
	rfid::RFIDinit(&myCallback);
	rfid::ReaderID reader = rfid::RFIDstartReader("tmr:///dev/rfid");

	std::cin.get();

	rfid::RFIDstopReader(reader);
	rfid::RFIDclose();
	return 0;
}
