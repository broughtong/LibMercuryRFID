#include <rfid_sensor_layer/rfid_sensor_layer.h>
#include <boost/algorithm/string.hpp>
#include <pluginlib/class_list_macros.h>
#include <angles/angles.h>
#include <math.h>

PLUGINLIB_EXPORT_CLASS(rfid_sensor_layer::RFIDSensorLayer, costmap_2d::Layer)

using costmap_2d::NO_INFORMATION;

namespace rfid_sensor_layer
{

RFIDSensorLayer::RFIDSensorLayer() {}

void RFIDSensorLayer::onInitialize()
{
  ros::NodeHandle nh("~/" + name_);
  current_ = true;
  buffered_readings_ = 0;
  last_reading_time_ = ros::Time::now();
  default_value_ = to_cost(0.5);

  matchSize();
  min_x_ = min_y_ = -std::numeric_limits<double>::max();
  max_x_ = max_y_ = std::numeric_limits<double>::max();

  // Default topic names list contains a single topic: lastTag
  // We use the XmlRpcValue constructor that takes a XML string and reading start offset
  const char* xml = "<value><array><data><value>/lastTag</value></data></array></value>";
  int zero_offset = 0;
  std::string topics_ns;
  XmlRpc::XmlRpcValue topic_names(xml, &zero_offset);

  nh.param("ns", topics_ns, std::string());
  nh.param("topics", topic_names, topic_names);

  //todo removed input sensor type... 

  // Validate topic names list: it must be a (normally non-empty) list of strings
  if ((topic_names.valid() == false) || (topic_names.getType() != XmlRpc::XmlRpcValue::TypeArray))
  {
    ROS_ERROR("Invalid topic names list: it must be a non-empty list of strings");
    return;
  }

  if (topic_names.size() < 1)
  {
    // This could be an error, but I keep it as it can be useful for debug
    ROS_WARN("Empty topic names list: rfid sensor layer will have no effect on costmap");
  }

  // Traverse the topic names list subscribing to all of them with the same callback method
  for (unsigned int i = 0; i < topic_names.size(); i++)
  {
    if (topic_names[i].getType() != XmlRpc::XmlRpcValue::TypeString)
    {
      ROS_WARN("Invalid topic names list: element %d is not a string, so it will be ignored", i);
    }
    else
    {
      std::string topic_name(topics_ns);
      if ((topic_name.size() > 0) && (topic_name.at(topic_name.size() - 1) != '/'))
        topic_name += "/";
      topic_name += static_cast<std::string>(topic_names[i]);

      processRFIDMessageFunc_ = boost::bind(&RFIDSensorLayer::processRFIDMsg, this, _1);
      
      rfid_subs_.push_back(nh.subscribe(topic_name, 100, &RFIDSensorLayer::bufferIncomingRFIDMsg, this));

      ROS_INFO("RFIDSensorLayer: subscribed to topic %s", rfid_subs_.back().getTopic().c_str());
    }
  }

  dsrv_ = new dynamic_reconfigure::Server<rfid_sensor_layer::RFIDSensorLayerConfig>(nh);
  dynamic_reconfigure::Server<rfid_sensor_layer::RFIDSensorLayerConfig>::CallbackType cb = boost::bind(
      &RFIDSensorLayer::reconfigureCB, this, _1, _2);
  dsrv_->setCallback(cb);
  global_frame_ = layered_costmap_->getGlobalFrameID();
}

// TODO unimplemented! this method should return a probability of getting reading 'data' at a relative distance and bearing.
double RFIDSensorLayer::sensor_model(double x_rel, double y_rel, double ang_rel, rfid_node::TagReading& data)
{
    double priorProb=1;
     
    double d2 = (x_rel*x_rel+y_rel*y_rel);   
    if (d2!=0)
        priorProb=1/d2;
    
    priorProb*=(M_PI/2-abs(ang_rel))/(3*M_PI/2);
    
    
        return  priorProb;
}

void RFIDSensorLayer::reconfigureCB(rfid_sensor_layer::RFIDSensorLayerConfig &config, uint32_t level)
{

  ant_angle_ = config.ant_angle;
  max_range_ = config.max_range;
  no_readings_timeout_ = config.no_readings_timeout;
  clear_threshold_ = config.clear_threshold;
  mark_threshold_ = config.mark_threshold;

    
  if(enabled_ != config.enabled)
  {
    enabled_ = config.enabled;
    current_ = false;
  }
}

void RFIDSensorLayer::bufferIncomingRFIDMsg(const rfid_node::TagReadingConstPtr& rfid_message)
{
  boost::mutex::scoped_lock lock(rfid_message_mutex_);
  rfid_msgs_buffer_.push_back(*rfid_message);
}

void RFIDSensorLayer::updateCostmap()
{
  std::list<rfid_node::TagReading> rfid_msgs_buffer_copy;

  rfid_message_mutex_.lock();
  rfid_msgs_buffer_copy = std::list<rfid_node::TagReading>(rfid_msgs_buffer_);
  rfid_msgs_buffer_.clear();
  rfid_message_mutex_.unlock();

  for (std::list<rfid_node::TagReading>::iterator rfid_msgs_it = rfid_msgs_buffer_copy.begin();
      rfid_msgs_it != rfid_msgs_buffer_copy.end(); rfid_msgs_it++)
  {
// a.k.a. RFIDSensorLayer::processRFIDMsg
    processRFIDMessageFunc_(*rfid_msgs_it);
  }
}

void RFIDSensorLayer::processRFIDMsg(rfid_node::TagReading& rfid_message)
{
  
  // here we should check if tagdata is valid...

  updateCostmap(rfid_message);
}

// TODO unimplemented! this method should determine the boundings and make updating
void RFIDSensorLayer::updateCostmap(rfid_node::TagReading& rfid_message)
{
  double max_angle_ = ant_angle_/2; //TODO check...
  double max_dist_ = max_range_; //TODO this is max RFID reading distance...

  geometry_msgs::PointStamped in;
  geometry_msgs::PointStamped out;

  // TODO rfid TagReading does not contain headers... we should add them!!
  in.header.stamp = rfid_message.header.stamp;
  in.header.frame_id = rfid_message.header.frame_id;

  if(!tf_->waitForTransform(global_frame_, in.header.frame_id,
        in.header.stamp, ros::Duration(0.1)) ) {
     ROS_ERROR_THROTTLE(1.0, "RFID sensor layer can't transform from %s to %s at %f",
        global_frame_.c_str(), in.header.frame_id.c_str(),
        in.header.stamp.toSec());
     return;
  }

  //get robot position 
  tf_->transformPoint (global_frame_, in, out);
  double ox = out.point.x;
  double oy = out.point.y;

  //get rfid range...
  in.point.x = max_dist_ ;
  tf_->transformPoint(global_frame_, in, out);
  double tx = out.point.x;
  double ty = out.point.y;

  // calculate target props
  double dx = tx-ox;
  double dy = ty-oy;
  double theta = atan2(dy,dx);
  double d = sqrt(dx*dx+dy*dy);

  // Integer Bounds of Update
  int bx0, by0, bx1, by1;

  // Bounds includes the origin
  worldToMapNoBounds(ox, oy, bx0, by0);
  bx1 = bx0;
  by1 = by0;
  touch(ox, oy, &min_x_, &min_y_, &max_x_, &max_y_);

  // Update Map with Target Point
  unsigned int aa, ab;
  if(worldToMap(tx, ty, aa, ab)){
    setCost(aa, ab, 233);
    touch(tx, ty, &min_x_, &min_y_, &max_x_, &max_y_);
  }

  double mx, my;
  int a, b;

  // Update left side of sonar cone
  mx = ox + cos(theta-max_angle_) * d * 1.2;
  my = oy + sin(theta-max_angle_) * d * 1.2;
  worldToMapNoBounds(mx, my, a, b);
  bx0 = std::min(bx0, a);
  bx1 = std::max(bx1, a);
  by0 = std::min(by0, b);
  by1 = std::max(by1, b);
  touch(mx, my, &min_x_, &min_y_, &max_x_, &max_y_);

  // Update right side of sonar cone
  mx = ox + cos(theta+max_angle_) * d * 1.2;
  my = oy + sin(theta+max_angle_) * d * 1.2;

  worldToMapNoBounds(mx, my, a, b);
  bx0 = std::min(bx0, a);
  bx1 = std::max(bx1, a);
  by0 = std::min(by0, b);
  by1 = std::max(by1, b);
  touch(mx, my, &min_x_, &min_y_, &max_x_, &max_y_);

  // Limit Bounds to Grid
  bx0 = std::max(0, bx0);
  by0 = std::max(0, by0);
  bx1 = std::min((int)size_x_, bx1);
  by1 = std::min((int)size_y_, by1);

  for(unsigned int x=bx0; x<=(unsigned int)bx1; x++){
    for(unsigned int y=by0; y<=(unsigned int)by1; y++){
      double wx, wy;
      mapToWorld(x,y,wx,wy);
      update_cell(ox, oy, theta, rfid_message, wx, wy);
    }
  }

  buffered_readings_++;
  last_reading_time_ = ros::Time::now();
}

void RFIDSensorLayer::update_cell(double origin_x, double origin_y, double origin_tetha, 
				rfid_node::TagReading& rfid_message, double updatePos_x, double updatePos_y)
{
  unsigned int x, y;
  if(worldToMap(updatePos_x, updatePos_y, x, y)){

    double dx = updatePos_x-origin_x;
    double dy = updatePos_y-origin_y;
    double theta = atan2(dy, dx) - origin_tetha;
    theta = angles::normalize_angle(theta);

    double sensor = sensor_model(dx,dy,theta,rfid_message);

    double prior = to_prob(getCost(x,y));
    double prob_occ = sensor * prior;
    double prob_norigin_tetha = (1 - sensor) * (1 - prior);
    double new_prob = prob_occ/(prob_occ+prob_norigin_tetha);

      unsigned char c = to_cost(new_prob);
      setCost(x,y,c);
  }
}

void RFIDSensorLayer::updateBounds(double robot_x, double robot_y, double robot_yaw, double* min_x,
                                           double* min_y, double* max_x, double* max_y)
{
  if (layered_costmap_->isRolling())
    updateOrigin(robot_x - getSizeInMetersX() / 2, robot_y - getSizeInMetersY() / 2);

  updateCostmap();

  *min_x = std::min(*min_x, min_x_);
  *min_y = std::min(*min_y, min_y_);
  *max_x = std::max(*max_x, max_x_);
  *max_y = std::max(*max_y, max_y_);

  min_x_ = min_y_ = std::numeric_limits<double>::max();
  max_x_ = max_y_ = std::numeric_limits<double>::min();

  if (!enabled_)
  {
    current_ = true;
    return;
  }
  
  if (buffered_readings_ == 0)
  {
    if (no_readings_timeout_ > 0.0 &&
        (ros::Time::now() - last_reading_time_).toSec() > no_readings_timeout_)
    {
      ROS_WARN_THROTTLE(2.0, "No rfid readings received for %.2f seconds, " \
                             "while expected at least every %.2f seconds.",
               (ros::Time::now() - last_reading_time_).toSec(), no_readings_timeout_);
      current_ = false;
    }
  }

}

void RFIDSensorLayer::updateCosts(costmap_2d::Costmap2D& master_grid, int min_i, int min_j, int max_i,
                                          int max_j)
{
  if (!enabled_)
    return;

  unsigned char* master_array = master_grid.getCharMap();
  unsigned int span = master_grid.getSizeInCellsX();
  unsigned char clear = to_cost(clear_threshold_), mark = to_cost(mark_threshold_);

  for (int j = min_j; j < max_j; j++)
  {
    unsigned int it = j * span + min_i;
    for (int i = min_i; i < max_i; i++)
    {
      unsigned char prob = costmap_[it];
      unsigned char current;
      if(prob==costmap_2d::NO_INFORMATION){
        it++;
        continue;
      }
      else if(prob>mark)
        current = costmap_2d::LETHAL_OBSTACLE;
      else if(prob<clear)
        current = costmap_2d::FREE_SPACE;
      else{
        it++;
        continue;
      }

      unsigned char old_cost = master_array[it];

      if (old_cost == NO_INFORMATION || old_cost < current)
        master_array[it] = current;
      it++;
    }
  }

  buffered_readings_ = 0;
  current_ = true;
}

void RFIDSensorLayer::reset()
{
  ROS_DEBUG("Reseting rfid sensor layer...");
  deactivate();
  resetMaps();
  current_ = true;
  activate();
}

} // end namespace
