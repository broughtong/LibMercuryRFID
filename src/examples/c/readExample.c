//compile with a g++ readExample.cpp -lmercuryrfid
//then a sudo ./a.out

//#include <iostream>
//#include "rfid.h"

#include <stdio.h>

void myCallback(const char* message)
{
	printf("%s\n", message);
}

int main(int argc, char *argv[])
{
	RFIDinit(&myCallback);
	int reader = RFIDstartReader("tmr:///dev/rfid");

	getchar();

	RFIDstopReader(reader);
	RFIDclose();

	return 0;
}
