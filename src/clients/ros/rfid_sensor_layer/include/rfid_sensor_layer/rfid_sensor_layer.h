#ifndef RFID_SENSOR_LAYER_H_
#define RFID_SENSOR_LAYER_H_
#include <ros/ros.h>
#include <costmap_2d/costmap_layer.h>
#include <costmap_2d/layered_costmap.h>
#include <rfid_node/TagReading.h>
#include <rfid_sensor_layer/RFIDSensorLayerConfig.h>
#include <dynamic_reconfigure/server.h>

namespace rfid_sensor_layer
{

class RFIDSensorLayer : public costmap_2d::CostmapLayer
{
public:

  RFIDSensorLayer();

  virtual void onInitialize();
  virtual void updateBounds(double robot_x, double robot_y, double robot_yaw, double* min_x,
                                           double* min_y, double* max_x, double* max_y);
                             
  virtual void updateCosts(costmap_2d::Costmap2D& master_grid, int min_i, int min_j, int max_i,
                                          int max_j);


private:
  void reconfigureCB(rfid_sensor_layer::RFIDSensorLayerConfig &config, uint32_t level);

  void bufferIncomingRFIDMsg(const rfid_node::TagReadingConstPtr& rfid_message);
  void processRFIDMsg(rfid_node::TagReading& rfid_message);
  
  void updateCostmap();
  void updateCostmap(rfid_node::TagReading& rfid_message);

  double sensor_model(double x_rel, double y_rel, double ang_rel, rfid_node::TagReading& data);
  
  void update_cell(double origin_x, double origin_y, double origin_tetha, 
				rfid_node::TagReading& rfid_message, double updatePos_x, double updatePos_y);
                
  void reset();

  double to_prob(unsigned char c){ return double(c)/costmap_2d::LETHAL_OBSTACLE; }
  unsigned char to_cost(double p){ return (unsigned char)(p*costmap_2d::LETHAL_OBSTACLE); }


  boost::function<void (rfid_node::TagReading& rfid_message)> processRFIDMessageFunc_;
  boost::mutex rfid_message_mutex_;
  std::list<rfid_node::TagReading> rfid_msgs_buffer_;

  double max_range_;
  double ant_angle_;
  std::string global_frame_;

  double clear_threshold_;
  double mark_threshold_;
  bool clear_on_max_reading_;

  double no_readings_timeout_;
  ros::Time last_reading_time_;
  unsigned int buffered_readings_;
  std::vector<ros::Subscriber> rfid_subs_;
  double min_x_, min_y_, max_x_, max_y_;

  dynamic_reconfigure::Server<rfid_sensor_layer::RFIDSensorLayerConfig> *dsrv_;
};
}
#endif








