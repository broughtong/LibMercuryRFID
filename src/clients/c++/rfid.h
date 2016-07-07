namespace rfid
{
	typedef int ReaderID;
	typedef void (*ForeignCallback)(const char* message);

	void init(rfid::ForeignCallback callbackHandle);
	rfid::ReaderID startReader(const char* deviceURI);
	void stopReader(rfid::ReaderID readerID);
	void close();

	extern "C"
	{
		int RFIDinit(ForeignCallback callbackHandle);
		int RFIDclose();
		int RFIDstartReader(const char* deviceURI);
		int RFIDstopReader(rfid::ReaderID readerID);
	}
}


