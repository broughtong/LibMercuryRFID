namespace rfid{

	typedef int ReaderID;

	void init();
	void close();
	ReaderID startReader(const char* deviceURI, void(*callbackFunction)(char* message));
	void stopReader(ReaderID readerID);

	void callbackHandler(char* char_ptr);
}
