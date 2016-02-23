namespace rfid{
	typedef int ReaderID;

	void init();
	ReaderID startReader();
	void stopReader();
	void close();
}
