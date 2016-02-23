int startReader(const char* deviceURI, void* callbackHandle);
int stopReader(int readerID);
int closeRFID();

namespace rfid
{
	void init();
	int startReader(const char* deviceURI, void* callbackFunction);
	void stopReader(int readerID);
	void close();
}
