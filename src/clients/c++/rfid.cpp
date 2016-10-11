#include "rfid.h"
#include <iostream>

namespace rfid{

	extern "C"
	{
		int RFIDinit(void (*callback)(char* message));
		int RFIDclose();
		int RFIDstartReader(const char* deviceURI);
		int RFIDstopReader(int readerID);
		//int RFIDpauseReader(ReaderID readerID);
		//int RFIDunpauseReader(ReaderID readerID);
	}

	void init()
	{
		RFIDinit(&callbackHandler);
	}

	void close()
	{
		RFIDclose();
	}

	ReaderID startReader(const char* deviceURI, void(*callbackFunction)(char* message))
	{
		ReaderID readerID = RFIDstartReader(deviceURI);

		return readerID;
	}

	void stopReader(ReaderID readerID)
	{
		RFIDstopReader(readerID);
	}

	void callbackHandler(char* char_ptr)
	{
		std::cout << "Message from cpp client: ";
		std::cout << char_ptr << std::endl;
	}
}
