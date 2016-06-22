    
/**
 * 
 * 
 * 
 * */


#include "rfid_grid_map/rfid_gridMap.hpp"


namespace rfid_grid_map {
    rfid_gridMap::rfid_gridMap(ros::NodeHandle& n)
    : nodeHandle_(n),
      map_(vector<string>({"type"}))
    {
        
      ROS_INFO("HI WORLD");
      //parameters (in meters)
      // map Size 
      double size_x=10;
      double size_y=10;
      // map resolution
      double resolution=0.1;
      intensity_=0.001;
  
      //2d position of the grid map in the grid map frame [m].  
      double orig_x=0;
      double orig_y=0;

  
      // Setting up map. 
      map_.setGeometry(Length(size_x, size_y), resolution, Position(orig_x, orig_y));
      map_.setFrameId("odom_combined");
      map_.clearAll();
      
      gridMapPublisher_ = nodeHandle_.advertise<grid_map_msgs::GridMap>("grid_map", 1, true);      
      publishMap();

  
      
        
      ros::Subscriber sub_ = n.subscribe("/lastTag", 1000, &rfid_gridMap::tagCallback, this);
      
      ros::Timer timer = n.createTimer(ros::Duration(0.5),  &rfid_gridMap::timerCallback,this);
      
      ros::Timer timer2 = n.createTimer(ros::Duration(1),  &rfid_gridMap::timerCallback2,this);
      
      ros::spin(); 
       
    }

    rfid_gridMap::~rfid_gridMap(){}
    
    
    void rfid_gridMap::tagCallback(const rfid_node::TagReading::ConstPtr& msg)
    {
       //ROS_INFO("I heard: tags! (%s,%d,%d,%d,%d,%s",msg->ID.c_str(),msg->rssi,msg->phase,msg->frequency,msg->txP,msg->header.frame_id.c_str());
       
       //ROS_INFO("Asking for location");
       updateTransform();
       //ROS_INFO("Location updated");       
       //where to plot circle (m)
       double x=transform_.getOrigin().x();
       double y=transform_.getOrigin().y();
       //ROS_INFO("I'm at %2.2f, %2.2f",x,y);
       
       //how big we want it (m)
       double radius=2;
    
    
       drawSquare(-5,-5,5,5,-intensity_);
       if (msg->ID.compare("390000010000000000000007")==0)
            drawCircle( x,  y,  radius, 5*intensity_);

       
    }
    
    void rfid_gridMap::timerCallback(const ros::TimerEvent&)
    {
     //ROS_INFO("UPDATE MAP NEEDED!");
     drawSquare(-5,-5,5,5,-intensity_);

     publishMap();
     }
    
    void rfid_gridMap::timerCallback2(const ros::TimerEvent&)
    {
        double total=0;
        double val1=0;
        double val2=0;
        double val3=0;
        double val4=0;
        // get total fddp
        total=countValuesInArea(-5,-5, 5, 5);
        val1 =countValuesInArea( 0, 0, 5, 5);
        val2 =countValuesInArea(-5, 0, 0, 5);
        val3 =countValuesInArea(-5,-5, 0, 0);
        val4 =countValuesInArea( 0,-5, 5, 0);
        ROS_INFO("Prob in region:");
        ROS_INFO("\t 1 is %2.2f",val1/total);
        ROS_INFO("\t 2 is %2.2f",val2/total);
        ROS_INFO("\t 3 is %2.2f",val3/total);
        ROS_INFO("\t 4 is %2.2f",val4/total);
    }
    
    void rfid_gridMap::updateTransform()
    {
        // TODO these are NOT frame ids 
        try{
            listener_.lookupTransform("odom_combined", "base_link", ros::Time(0), transform_);
        }
        catch (tf::TransformException ex){
            ROS_ERROR("%s",ex.what());
            ros::Duration(1.0).sleep();
        }    
    }
    
    
    void rfid_gridMap::publishMap()
    {
      
      map_.setTimestamp(ros::Time::now().toNSec());
      
      grid_map_msgs::GridMap message;
      grid_map::GridMapRosConverter::toMessage(map_, message);
      gridMapPublisher_.publish(message);
      ROS_DEBUG("Grid map (timestamp %f) published.", message.info.header.stamp.toSec());
    }


    // based on demoSubMapIterator
double rfid_gridMap::countValuesInArea(double start_x,double start_y,double end_x,double end_y)
{
  Index submapStartIndex;
  Index submapEndIndex;
  Index submapBufferSize;
  
  Index lowerCorner(0,0);
  Index upperCorner(0,0);
  
  double total=0.0;
  
  Position position;
  
  Position submapStartPosition(end_x, end_y);
  Position submapEndPosition(start_x, start_y);  
  
  Size mapSize=map_.getSize();
  //ROS_INFO("Map is (%d w %d h)",mapSize(0),mapSize(1));
  upperCorner(0)=  mapSize(0)-1;
  upperCorner(1)=  mapSize(1)-1;  
  
  if (!map_.isInside(submapStartPosition)){
      //ROS_INFO("Start Position is out of map");
      map_.getPosition( lowerCorner, position ) ;
        
      //rounding
      if (submapStartPosition(0)<position(0))
            submapStartPosition(0)=position(0);
      if (submapStartPosition(1)<position(1))
            submapStartPosition(1)=position(1);
      
      //ROS_INFO("Accessing  from position (%2.2f,%2.2f) ",submapStartPosition(0),submapStartPosition(1) );    
  }
  if (!map_.isInside(submapEndPosition)){
      //ROS_INFO("End Position is out of map");
       map_.getPosition( upperCorner, position ) ;
        
      //rounding
      if (submapEndPosition(0)<position(0))
            submapEndPosition(0)=position(0);
      if (submapEndPosition(1)<position(1))
            submapEndPosition(1)=position(1);
      
      //ROS_INFO("Accessing up to position (%2.2f,%2.2f)",submapEndPosition(0),submapEndPosition(1) );    
  }
  
  map_.getIndex(submapStartPosition,submapStartIndex);
  map_.getIndex(submapEndPosition,submapEndIndex);
 //ROS_INFO("Accessing  from index (%d,%d) to (%d,%d)",submapStartIndex(0),submapStartIndex(1),submapEndIndex(0),submapEndIndex(1) );    
      
  submapBufferSize=abs(submapEndIndex-submapStartIndex);
  
 // ROS_INFO("Accessing (%d width x %d high) indexes",submapBufferSize(0),submapBufferSize(1));    
  for (grid_map::SubmapIterator iterator(map_, submapStartIndex, submapBufferSize);
      !iterator.isPastEnd(); ++iterator) {              
        //map_.getPosition( *iterator, position ) ;	          
        if (!isnan(map_.at("type", *iterator)))
        {
            total+=map_.at("type", *iterator);
            //ROS_INFO("Cell(%1f,%1f) val is %2.2f",position(0),position(1),map_.at("type", *iterator));
        }
  }

  return total;
}

void rfid_gridMap::drawSquare(double start_x,double start_y,double end_x,double end_y,double value)
{
  Index submapStartIndex;
  Index submapEndIndex;
  Index submapBufferSize;
  
  Index lowerCorner(0,0);
  Index upperCorner(0,0);
    
  Position position;
  
  Position submapStartPosition(end_x, end_y);
  Position submapEndPosition(start_x, start_y);  
  
  Size mapSize=map_.getSize();
  //ROS_INFO("Map is (%d w %d h)",mapSize(0),mapSize(1));
  upperCorner(0)=  mapSize(0)-1;
  upperCorner(1)=  mapSize(1)-1;  
  
  if (!map_.isInside(submapStartPosition)){
      //ROS_INFO("Start Position is out of map");
      map_.getPosition( lowerCorner, position ) ;
        
      //rounding
      if (submapStartPosition(0)<position(0))
            submapStartPosition(0)=position(0);
      if (submapStartPosition(1)<position(1))
            submapStartPosition(1)=position(1);
      
      //ROS_INFO("Accessing  from position (%2.2f,%2.2f) ",submapStartPosition(0),submapStartPosition(1) );    
  }
  if (!map_.isInside(submapEndPosition)){
      //ROS_INFO("End Position is out of map");
       map_.getPosition( upperCorner, position ) ;
        
      //rounding
      if (submapEndPosition(0)<position(0))
            submapEndPosition(0)=position(0);
      if (submapEndPosition(1)<position(1))
            submapEndPosition(1)=position(1);
      
      //ROS_INFO("Accessing up to position (%2.2f,%2.2f)",submapEndPosition(0),submapEndPosition(1) );    
  }
  
  map_.getIndex(submapStartPosition,submapStartIndex);
  map_.getIndex(submapEndPosition,submapEndIndex);
 //ROS_INFO("Accessing  from index (%d,%d) to (%d,%d)",submapStartIndex(0),submapStartIndex(1),submapEndIndex(0),submapEndIndex(1) );    
      
  submapBufferSize=abs(submapEndIndex-submapStartIndex);
  
 // ROS_INFO("Accessing (%d width x %d high) indexes",submapBufferSize(0),submapBufferSize(1));    
  for (grid_map::SubmapIterator iterator(map_, submapStartIndex, submapBufferSize);
      !iterator.isPastEnd(); ++iterator) {     
        
        map_.at("type", *iterator) =  value +map_.at("type", *iterator);              
        if (isnan(map_.at("type", *iterator)))
        {
            map_.at("type", *iterator) =  value;
        }
        if (map_.at("type", *iterator)<0.0)
            map_.at("type", *iterator) =  0.0;
  }

}


// based on demoCircleIterator
void rfid_gridMap::drawCircle(double x, double y, double radius, double value)
{
  //ROS_INFO("Plotting circle at (%2.2f,%2.2f)",x,y);
  
  Position center(x, y);
  
  for (grid_map::CircleIterator iterator(map_, center, radius);
      !iterator.isPastEnd(); ++iterator) {
    map_.at("type", *iterator) =  value +map_.at("type", *iterator);
    
    if (isnan(map_.at("type", *iterator)))
    {
        map_.at("type", *iterator) =  value;
    }    
    if (map_.at("type", *iterator)<0.0)
        map_.at("type", *iterator) =  0.0;
    
  }
}
    
    
} // end of namespace rfid_grid_map
