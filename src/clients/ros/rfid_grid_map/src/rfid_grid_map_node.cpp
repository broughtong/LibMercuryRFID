    
/*
 */

#include "rfid_grid_map/rfid_gridMap.hpp"

int main(int argc, char** argv)
{
  ros::init(argc, argv, "rfid_grid_map_node");

  ros::NodeHandle nd("~");
  rfid_grid_map::rfid_gridMap rg(nd);

  ros::requestShutdown();
  return 0;
}
