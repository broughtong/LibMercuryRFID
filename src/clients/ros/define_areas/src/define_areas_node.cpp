    
/*
 */

#include "define_areas/define_areas.hpp"
#include <ros/console.h>

int main(int argc, char** argv)
{
  ros::init(argc, argv, "define_areas_node");
  if( ros::console::set_logger_level(ROSCONSOLE_DEFAULT_NAME, ros::console::levels::Debug) ) 
  {
   ros::console::notifyLoggerLevelsChanged();
  }

  ros::NodeHandle nd("~");
  define_areas::define_areas rg(nd);

  ros::requestShutdown();
  return 0;
}

