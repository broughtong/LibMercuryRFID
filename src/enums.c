int getEnum(const char* string)
{
	if("TMR_PARAM_NONE")
	{
		return 0;
	}
	else if("TMR_PARAM_MIN")
	{
			return 1;
	}
	else if("TMR_PARAM_BAUDRATE")
	{
			return 1;
	}
	else if("TMR_PARAM_PROBEBAUDRATES")
	{
			return 2;
	}
	else if("TMR_PARAM_COMMANDTIMEOUT")
	{
			return 3;
	}
	else if("TMR_PARAM_TRANSPORTTIMEOUT")
	{
			return 4;
	}
	else if("TMR_PARAM_POWERMODE")
	{
			return 5;
	}
	else if("TMR_PARAM_USERMODE")
	{
			return 6;
	}
	else if("TMR_PARAM_ANTENNA_CHECKPORT")
	{
			return 7;
	}
	else if("TMR_PARAM_ANTENNA_PORTLIST")
	{
			return 8;
	}
	else if("TMR_PARAM_ANTENNA_CONNECTEDPORTLIST")
	{
			return 9;
	}
	else if("TMR_PARAM_ANTENNA_PORTSWITCHGPOS")
	{
			return 10;
	}
	else if("TMR_PARAM_ANTENNA_SETTLINGTIMELIST")
	{
			return 11;
	}
	else if("TMR_PARAM_ANTENNA_RETURNLOSS")
	{
			return 12;
	}
	else if("TMR_PARAM_ANTENNA_TXRXMAP")
	{
			return 13;
	}
	else if("TMR_PARAM_GPIO_INPUTLIST")
	{
			return 14;
	}
	else if("TMR_PARAM_GPIO_OUTPUTLIST")
	{
			return 15;
	}
	else if("TMR_PARAM_GEN2_ACCESSPASSWORD")
	{
			return 16;
	}
	else if("TMR_PARAM_GEN2_Q")
	{
			return 17;
	}
	else if("TMR_PARAM_GEN2_TAGENCODING")
	{
			return 18;
	}
	else if("TMR_PARAM_GEN2_SESSION")
	{
			return 19;
	}
	else if("TMR_PARAM_GEN2_TARGET")
	{
			return 20;
	}
	else if("TMR_PARAM_GEN2_BLF")
	{
			return 21;
	}
	else if("TMR_PARAM_GEN2_TARI")
	{
			return 22;
	}
	else if("TMR_PARAM_GEN2_WRITEMODE")
	{
			return 23;
	}
	else if("TMR_PARAM_GEN2_BAP")
	{
			return 24;
	}
	else if("TMR_PARAM_ISO180006B_BLF")
	{
			return 25;
	}
	else if("TMR_PARAM_ISO180006B_MODULATION_DEPTH")
	{
			return 26;
	}
	else if("TMR_PARAM_ISO180006B_DELIMITER")
	{
			return 27;
	}
	else if("TMR_PARAM_READ_ASYNCOFFTIME")
	{
			return 28;
	}
	else if("TMR_PARAM_READ_ASYNCONTIME")
	{
			return 29;
	}
	else if("TMR_PARAM_READ_PLAN")
	{
			return 30;
	}
	else if("TMR_PARAM_RADIO_ENABLEPOWERSAVE")
	{
			return 31;
	}
	else if("TMR_PARAM_RADIO_POWERMAX")
	{
			return 32;
	}
	else if("TMR_PARAM_RADIO_POWERMIN")
	{
			return 33;
	}
	else if("TMR_PARAM_RADIO_PORTREADPOWERLIST")
	{
			return 34;
	}
	else if("TMR_PARAM_RADIO_PORTWRITEPOWERLIST")
	{
			return 35;
	}
	else if("TMR_PARAM_RADIO_READPOWER")
	{
			return 36;
	}
	else if("TMR_PARAM_RADIO_WRITEPOWER")
	{
			return 37;
	}
	else if("TMR_PARAM_RADIO_TEMPERATURE")
	{
			return 38;
	}
	else if("TMR_PARAM_TAGREADDATA_RECORDHIGHESTRSSI")
	{
			return 39;
	}
	else if("TMR_PARAM_TAGREADDATA_REPORTRSSIINDBM")
	{
			return 40;
	}
	else if("TMR_PARAM_TAGREADDATA_UNIQUEBYANTENNA")
	{
			return 41;
	}
	else if("TMR_PARAM_TAGREADDATA_UNIQUEBYDATA")
	{
			return 42;
	}
	else if("TMR_PARAM_TAGOP_ANTENNA")
	{
			return 43;
	}
	else if("TMR_PARAM_TAGOP_PROTOCOL")
	{
			return 44;
	}
	else if("TMR_PARAM_VERSION_HARDWARE")
	{
			return 45;
	}
	else if("TMR_PARAM_VERSION_SERIAL")
	{
			return 46;
	}
	else if("TMR_PARAM_VERSION_MODEL")
	{
			return 47;
	}
	else if("TMR_PARAM_VERSION_SOFTWARE")
	{
			return 48;
	}
	else if("TMR_PARAM_VERSION_SUPPORTEDPROTOCOLS")
	{
			return 49;
	}
	else if("TMR_PARAM_REGION_HOPTABLE")
	{
			return 50;
	}
	else if("TMR_PARAM_REGION_HOPTIME")
	{
			return 51;
	}
	else if("TMR_PARAM_REGION_ID")
	{
			return 52;
	}
	else if("TMR_PARAM_REGION_SUPPORTEDREGIONS")
	{
			return 53;
	}
	else if("TMR_PARAM_REGION_LBT_ENABLE")
	{
			return 54;
	}
	else if("TMR_PARAM_LICENSE_KEY")
	{
			return 55;
	}
	else if("TMR_PARAM_USER_CONFIG")
	{
			return 56;
	}
	else if("TMR_PARAM_RADIO_ENABLESJC")
	{
			return 57;
	}
	else if("TMR_PARAM_EXTENDEDEPC")
	{
			return 58;
	}
	else if("TMR_PARAM_READER_STATISTICS")
	{
			return 59;
	}
	else if("TMR_PARAM_READER_STATS")
	{
			return 60;
	}
	else if("TMR_PARAM_URI")
	{
			return 61;
	}
	else if("TMR_PARAM_PRODUCT_GROUP_ID")
	{
			return 62;
	}
	else if("TMR_PARAM_PRODUCT_GROUP")
	{
			return 63;
	}
	else if("TMR_PARAM_PRODUCT_ID")
	{
			return 64;
	}
	else if("TMR_PARAM_TAGREADATA_TAGOPSUCCESSCOUNT")
	{
			return 65;
	}
	else if("TMR_PARAM_TAGREADATA_TAGOPFAILURECOUNT")
	{
			return 66;
	}
	else if("TMR_PARAM_STATUS_ENABLE_ANTENNAREPORT")
	{
			return 67;
	}
	else if("TMR_PARAM_STATUS_ENABLE_FREQUENCYREPORT")
	{
			return 68;
	}
	else if("TMR_PARAM_STATUS_ENABLE_TEMPERATUREREPORT")
	{
			return 69;
	}
	else if("TMR_PARAM_TAGREADDATA_ENABLEREADFILTER")
	{
			return 70;
	}
	else if("TMR_PARAM_TAGREADDATA_READFILTERTIMEOUT")
	{
			return 71;
	}
	else if("TMR_PARAM_TAGREADDATA_UNIQUEBYPROTOCOL")
	{
			return 72;
	}
	else if("TMR_PARAM_READER_DESCRIPTION")
	{
			return 73;
	}
	else if("TMR_PARAM_READER_HOSTNAME")
	{
			return 74;
	}
	else if("TMR_PARAM_CURRENTTIME")
	{
			return 75;
	}
	else if("TMR_PARAM_READER_WRITE_REPLY_TIMEOUT")
	{
			return 76;
	}
	else if("TMR_PARAM_READER_WRITE_EARLY_EXIT")
	{
			return 77;
	}
	else if("TMR_PARAM_READER_STATS_ENABLE")
	{
			return 78;
	}
	else if("TMR_PARAM_TRIGGER_READ_GPI")
	{
			return 79;
	}
	else if("TMR_PARAM_MAX")
	{
			return 79;
	}
	else if("TMR_PARAM_END")
	{
			return 80;
	}
}
