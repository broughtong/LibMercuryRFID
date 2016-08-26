/**
 * 
 * 
 * 
 * 
 * */


    
#pragma once

#include <grid_map_ros/grid_map_ros.hpp>
//#include <math.h>  // isnan

#include <yaml-cpp/yaml.h>
// ROS
#include <ros/ros.h>
#include <ros/console.h>
#include <std_msgs/String.h>
#include <tf/transform_listener.h>
  
// #include <geometry_msgs/PolygonStamped.h> //for future use with more complex shapes
#include <rfid_node/TagReading.h>
//#include <std_msgs/Int16.h>


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
      void updateMapCallback(const ros::TimerEvent&);
    
      void updateProbs(const ros::TimerEvent&);
      
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
      
      //! publisher for probs
      ros::Publisher prob_pub_ ;
       
      //! map Size (in meters)
      double size_x; 
      double size_y;
      //! Grid map publisher.
      ros::Publisher gridMapPublisher_;

      tf::TransformListener listener_;
      tf::StampedTransform transform_;

      //! gridmap actualization rate .        
      double intensity_;
      //! regions description file 
      YAML::Node config ;
      //! rfid tag id
      std::string tagID;
      
      //! global frame id (for maps)
      std::string global_frame;
      //! robot frame id 
      std::string robot_frame;

}; // End of Class rfid_gridMap

} // end of  namespace rfid_grid_map
