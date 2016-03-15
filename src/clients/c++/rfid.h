namespace rfid{
	typedef int ReaderID;

	void init();
	ReaderID startReader();
	void stopReader();
	void close();

	extern "C"
	{
		int startReader(const char* deviceURI, void (*callback)(const char** message));
		int stopReader(int readerID);
		int closeRFID();
	}
}


