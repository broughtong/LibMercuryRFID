
#include <ros/ros.h>
#include <yaml-cpp/yaml.h>
#include <fstream>      // std::ofstream

using namespace ros;

std::string get_working_path()
{
   int MAXPATHLEN=512;
   char temp[MAXPATHLEN];
   return ( getcwd(temp, MAXPATHLEN) ? std::string( temp ) : std::string("") );
}

int main(int argc,char **argv){

  ros::init(argc, argv, "yamltest");
  ros::NodeHandle node;
  ros::NodeHandle priv_nh("~");
  std::cout <<  get_working_path() << "\n";
 
  YAML::Node config = YAML::LoadFile("/home/mfcarmona/catkin_ws/src/yamltest/cfg/LCAS.yaml");

  
  int i;
  for (std::size_t i=0;i<config["Regions"].size();i++) {
     std::cout << config["Regions"][i]["name"] << "\n";
     std::cout << config["Regions"][i]["min"]["x"] <<", "<< config["Regions"][i]["min"]["y"] << "\n";
     std::cout << config["Regions"][i]["max"]["x"] <<", "<< config["Regions"][i]["max"]["y"] << "\n";
     
     if (config["Regions"][i]["subregions"]){
		 int j;
		   for (std::size_t j=0;j<config["Regions"][i]["subregions"].size();j++) {
			   std::cout << config["Regions"][i]["subregions"][j]["name"] << "\n";		   
               std::cout << config["Regions"][i]["subregions"][j]["min"]["x"] <<", "<< config["Regions"][i]["subregions"][j]["min"]["y"] << "\n";
               std::cout << config["Regions"][i]["subregions"][j]["max"]["x"] <<", "<< config["Regions"][i]["subregions"][j]["max"]["y"] << "\n";
		   }
		 
		 
	 }
  }

/*  YAML::Node mapDesc;  // starts out as null

  mapDesc["mapName"] = "LCAS Lab"; 

///////////////////////////
  YAML::Node region;
  region["name"] = "kitchen"; 
  region["min"]["x"]=0.0;
  region["min"]["y"]=0.0;
  region["max"]["x"]=1.0;
  region["max"]["y"]=1.0;
   //......................................
  YAML::Node subregion;
  subregion["name"] = "kitchen fridge"; 
  subregion["min"]["x"]=0.0;
  subregion["min"]["y"]=0.0;
  subregion["max"]["x"]=1.0;
  subregion["max"]["y"]=0.5;
  
  region["subregions"].push_back(subregion);
  //........................................
  YAML::Node subregion2;
  subregion2["name"] = "kitchen cook"; 
  subregion2["min"]["x"]=0.0;
  subregion2["min"]["y"]=0.5;
  subregion2["max"]["x"]=1.0;
  subregion2["max"]["y"]=1.0;
  
  region["subregions"].push_back(subregion2);
  //........................................  
  mapDesc["Regions"].push_back(region); 
  
  
///////////////////////////
  YAML::Node region2;
  region2["name"] = "living"; 
  region2["min"]["x"]=0.0;
  region2["min"]["y"]=1.0;
  region2["max"]["x"]=1.0;
  region2["max"]["y"]=2.0;
   //......................................
  YAML::Node sub2region;
  sub2region["name"] = "living coach"; 
  sub2region["min"]["x"]=0.0;
  sub2region["min"]["y"]=1.0;
  sub2region["max"]["x"]=1.0;
  sub2region["max"]["y"]=1.5;
  
  region2["subregions"].push_back(sub2region);
  //........................................
  YAML::Node sub2region2;
  sub2region2["name"] = "living table"; 
  sub2region2["min"]["x"]=0.0;
  sub2region2["min"]["y"]=1.5;
  sub2region2["max"]["x"]=1.0;
  sub2region2["max"]["y"]=2.0;
  
  region2["subregions"].push_back(sub2region2);
  //........................................  
  mapDesc["Regions"].push_back(region2); 
  
  ///////////////////////////
  YAML::Node region3;
  region3["name"] = "bathroom"; 
  region3["min"]["x"]=1.0;
  region3["min"]["y"]=0.0;
  region3["max"]["x"]=2.0;
  region3["max"]["y"]=1.0;
  mapDesc["Regions"].push_back(region3); 
  
  std::cout << mapDesc<<"\n";
  
  std::ofstream fout("/home/mfcarmona/catkin_ws/src/yamltest/cfg/LCAS.yaml"); 
  fout << mapDesc;
  fout.close();*/
  
  // handle callbacks until shut down
  ros::spin();

return 0;
}
