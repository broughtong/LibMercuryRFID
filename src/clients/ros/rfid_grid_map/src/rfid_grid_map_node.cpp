    
/*
 */

#include "rfid_grid_map/rfid_gridMap.hpp"

int main(int argc, char** argv)
{
  ros::init(argc, argv, "rfid_grid_map_node");

  if( ros::console::set_logger_level(ROSCONSOLE_DEFAULT_NAME, ros::console::levels::Debug) ) 
  {
   ros::console::notifyLoggerLevelsChanged();
  }
  
  ros::NodeHandle nd("~");
  rfid_grid_map::rfid_gridMap rg(nd);
  
  
  ros::requestShutdown();
  return 0;
}
