/**
 * 
 * 
 * 
 * 
 * */


    
#pragma once

#include <grid_map_ros/grid_map_ros.hpp>
#include <list>
#include <yaml-cpp/yaml.h>


// ROS
#include <ros/ros.h>
#include <std_msgs/String.h>
#include "nav_msgs/GetMap.h"
#include "geometry_msgs/PointStamped.h"
#include "geometry_msgs/Point.h"

#include <visualization_msgs/Marker.h>
#include <nav_msgs/MapMetaData.h>

using namespace std;
using namespace ros;
using namespace grid_map;

namespace define_areas {

/*!
 
 */
class define_areas
{
    struct type_area{
        double startX;
        double startY;
        double endX;
        double endY;
        string name;
    };
    
    public:

      /*!
       * Constructor.
       * @param nodeHandle the ROS node handle.
       */
      define_areas(ros::NodeHandle& nodeHandle);

      ~define_areas();
      
      void drawSquare(double start_x,double start_y,double end_x,double end_y,double value);

      void publishMap();
      
      void mapCallback(const nav_msgs::OccupancyGrid& msg);
      
      void plotMarker(double x, double  y, string text );
    
     void timerCallback(const ros::TimerEvent&);
     
     void clickCallback(const geometry_msgs::PointStamped::ConstPtr msg);
     
     std::list<define_areas::type_area> loadAreas(std::string regions_file);
     
    private:
      //! ROS nodehandle.
      ros::NodeHandle& nodeHandle_;
      
      //! Grid map data.
      grid_map::GridMap map_;

      //! Grid map publisher.
      ros::Publisher gridMapPublisher_;

      bool isMapLoaded;
      
      nav_msgs::MapMetaData mapDesc;
      
      ros::Publisher vis_pub;
      
      int numberOfClicks;
      geometry_msgs::Point startPoint;
      geometry_msgs::Point endPoint;
  
}; // End of Class define_areas

} // end of  namespace define_areas
