# An inventory of tags.
#   startTime:       when it was started
#   endTime:         when was last tag detected
#   maxTimeMiliSecs  how long will be reader detecting tags
#   TxPower          transmission power for this inventory
#   tagList          array of detected tags and data


time      startTime
time      endTime
int32     maxTimeMiliSecs
int32     TxPower
TagData[] tagList
 
