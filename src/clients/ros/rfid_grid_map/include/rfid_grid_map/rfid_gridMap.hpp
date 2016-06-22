/**
 * 
 * 
 * 
 * 
 * */


    
#pragma once

#include <grid_map_ros/grid_map_ros.hpp>
//#include <math.h>  // isnan

// ROS
#include <ros/ros.h>
#include <std_msgs/String.h>
// #include <geometry_msgs/PolygonStamped.h> //for future use with more complex shapes
#include <rfid_node/TagReading.h>
//#include <std_msgs/Int16.h>
#include <tf/transform_listener.h>

using namespace std;
using namespace ros;
using namespace grid_map;

namespace rfid_grid_map {

/*!
 
 */
class rfid_gridMap
{
    public:

      /*!
       * Constructor.
       * @param nodeHandle the ROS node handle.
       */
      rfid_gridMap(ros::NodeHandle& nodeHandle);

      virtual ~rfid_gridMap();
      
      //! callback for rfid messages...
      void tagCallback(const rfid_node::TagReading::ConstPtr& msg);
    
      //! periodic map updates
      void timerCallback(const ros::TimerEvent&);
    
      void timerCallback2(const ros::TimerEvent&);
      
      void updateTransform();        
      
      void publishMap();
      
      double countValuesInArea(double start_x,double start_y,double end_x,double end_y);
      
      void drawSquare(double start_x,double start_y,double end_x,double end_y,double value);
      
      void drawCircle(double x, double y, double radius, double value);
    
    private:
      //! ROS nodehandle.
      ros::NodeHandle& nodeHandle_;
      
      //! ROS subscriber to rfid messages...
      ros::Subscriber sub_;
      //! Grid map data.
      grid_map::GridMap map_;
      //! Grid map publisher.
      ros::Publisher gridMapPublisher_;

      tf::TransformListener listener_;
      tf::StampedTransform transform_;
        
     double intensity_;
  
}; // End of Class rfid_gridMap

} // end of  namespace rfid_grid_map
