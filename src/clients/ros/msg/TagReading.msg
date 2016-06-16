# Tag data retrieved from rfid reader
# collected using node rfid_reader_ros
#
# header      
# ID          tag EPC code
# txP         transmitted power from reader
# timestamp   reader timestamp
# rssi        signal strength (dBm)
# phase       wave phase  (degrees)
# frequency   wave frequency (KHz)

Header header
string ID
int32  txP
time   timestamp
int32  rssi
int32  phase
int32  frequency

