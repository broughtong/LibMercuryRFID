# An inventory of tags.
#   startTime        when it was started
#   lastTagTime      when was last tag detected
#   readingTime      how long was reader trying to detect tags
#   TxPower          reading transmission power for this inventory
#   tagList          array of detected tags and data


time      startTime
time      lastTagTime
duration  readingTime
int32     TxPower
TagData[] tagList
 
