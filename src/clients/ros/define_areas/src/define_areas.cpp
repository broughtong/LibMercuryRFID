    
/**
 * 
 * 
 * 
 * */


#include "define_areas/define_areas.hpp"


namespace define_areas {

        
    define_areas::define_areas(ros::NodeHandle& n)
    : nodeHandle_(n),
      map_(vector<string>({"type"}))
    {
        
      ROS_DEBUG("HI WORLD");
      
      // connect to map server and get dimensions and resolution (meters)
      ROS_DEBUG("Waiting for map service");
      ros::service::waitForService("static_map");    
      // get map via RPC
      nav_msgs::GetMap::Request  req;
      nav_msgs::GetMap::Response resp;
      ROS_DEBUG("Requesting the map...");
      ros::service::call("static_map", req, resp);
      mapCallback(resp.map);
      
      // map resolution (m/cell)
      double resolution=mapDesc.resolution;    
      // map Size (m.)
      double size_x=2*mapDesc.height*resolution;
      double size_y=2*mapDesc.width*resolution;

      //2d position of the grid map in the grid map frame [m]. 
      // we consider them alligned 
      double orig_x=0;
      double orig_y=0;
    
  
      // Setting up map. 
      map_.setGeometry(Length(size_x, size_y), resolution, Position(orig_x, orig_y));
      map_.setFrameId("map");
      map_.clearAll();
      
      gridMapPublisher_ = nodeHandle_.advertise<grid_map_msgs::GridMap>("grid_map", 1, true);      
      publishMap();
      ROS_DEBUG("First grid published");
      vis_pub = nodeHandle_.advertise<visualization_msgs::Marker>( "visualization_marker", 0 );
  
      //subscribe to clicks
      numberOfClicks=-1;
      ros::Subscriber sub_ = n.subscribe("/clicked_point", 1000, &define_areas::clickCallback, this);

      std::string regions_file;
      
      ROS_ASSERT(nodeHandle_.getParam("regions_file", regions_file));          
      //nodeHandle_.param("regions_file", regions_file,std::string("/home/mfernandezcarmona/catkin_ws/src/ENRICHME/codes/ais/LibMercuryRFID/src/clients/ros/rfid_grid_map/config/LCAS.yaml"));    
      ROS_DEBUG("Loading config from %s",regions_file.c_str());

      

      // got to find a better way to do this...
      std::list<type_area> areas;
      
      areas=loadAreas(regions_file);
      
  


      int i=0;             
      
      for (std::list<type_area>::iterator area=areas.begin(); area != areas.end(); ++area)   
      {          
          ROS_DEBUG("Publishin region %s",area->name.c_str());
          drawSquare(area->startX,area->startY,area->endX,area->endY,0.5);
          plotMarker(  ( area->endX - area->startX ) / 2 ,( area->endY - area->startY) / 2, area->name );
          publishMap();
          ros::Duration d(2);
          d.sleep();
      }
      
      //ROS_DEBUG("Regions published");
      //ros::Timer timer = n.createTimer(ros::Duration(0.5),  &define_areas::timerCallback,this);

      ros::spin(); 
       
    }

    void define_areas::timerCallback(const ros::TimerEvent&)
    {
     //ROS_INFO("UPDATE MAP NEEDED!");
     //drawSquare(-5,-5,5,5,-intensity_);

     //publishMap();
     }
     
     std::list<define_areas::type_area> define_areas::loadAreas(std::string regions_file){
        int i=0;
        
        std::list<type_area> mapa;
        // regions description file 
        YAML::Node config ;
        // load regions yaml file      
        ROS_DEBUG("Loading config from %s",regions_file.c_str());
        config = YAML::LoadFile(regions_file);
        ROS_DEBUG("///////////////////////////////////////////////////////////////////////");
        ROS_DEBUG("Loading regions (#%d)\n",(int) config["Regions"].size());
        
        
        for (std::size_t i=0;i<config["Regions"].size();i++) {            
            type_area area;            
            area.name=config["Regions"][i]["name"].as<std::string>();;
            area.startX=config["Regions"][i]["min"]["x"].as<double>();;
            area.startY=config["Regions"][i]["min"]["y"].as<double>();;							
            area.endX=config["Regions"][i]["max"]["x"].as<double>();;
            area.endY=config["Regions"][i]["max"]["y"].as<double>();;
            mapa.push_back(area);
            
            ROS_DEBUG("-Region %s\n",area.name.c_str());
            ROS_DEBUG("  - name: %s\n    min:\n      x: %.2f\n      y: %.2f\n    max:\n      x: %.2f\n      y: %.2f\n\n",area.name.c_str(),area.startX,area.startY,area.endX,area.endY);    
            
            if (config["Regions"][i]["subregions"]){
                int j;
                for (std::size_t j=0;j<config["Regions"][i]["subregions"].size();j++) {
                    type_area area;
                    area.name=config["Regions"][i]["subregions"][j]["name"].as<std::string>();;
                    area.startX=config["Regions"][i]["subregions"][j]["min"]["x"].as<double>();;
                    area.startY=config["Regions"][i]["subregions"][j]["min"]["y"].as<double>();;							
                    area.endX=config["Regions"][i]["subregions"][j]["max"]["x"].as<double>();;
                    area.endY=config["Regions"][i]["subregions"][j]["max"]["y"].as<double>();;
                    mapa.push_back(area);
                    
                    ROS_DEBUG("-Subregion %s\n",area.name.c_str());
                    ROS_DEBUG("min:\nx: %.2f\ny: %.2f\n max:\nx: %.2f\ny: %.2f\n\n",area.startX,area.startY,area.endX,area.endY);    
                }	 
            }
            ROS_DEBUG("...................................................................");
        }
        ROS_DEBUG("///////////////////////////////////////////////////////////////////////");
        return mapa;
      
      }
      
      

      



     
    define_areas::~define_areas(){}
    
    void define_areas::plotMarker(double x, double  y, string text )
    {
        
        visualization_msgs::Marker marker;
        marker.header.frame_id = "map";
        marker.header.stamp = ros::Time();
        marker.ns = "my_namespace";
        marker.id = 0;
        marker.type = visualization_msgs::Marker::TEXT_VIEW_FACING;
        marker.action = visualization_msgs::Marker::ADD;
        marker.text=text;
        marker.pose.position.x = 1;
        marker.pose.position.y = 1;
        marker.pose.position.z = 1;
        marker.pose.orientation.x = 0.0;
        marker.pose.orientation.y = 0.0;
        marker.pose.orientation.z = 0.0;
        marker.pose.orientation.w = 1.0;
        marker.scale.x = 1;
        marker.scale.y = 0.1;
        marker.scale.z = 0.1;
        marker.color.a = 1.0; // Don't forget to set the alpha!
        marker.color.r = 0.0;
        marker.color.g = 1.0;
        marker.color.b = 0.0;
        marker.lifetime= ros::Duration(0);
        vis_pub.publish( marker );

    }
    
    // we get information from our global map
    void define_areas::mapCallback(const nav_msgs::OccupancyGrid& msg)
    {
        isMapLoaded=true;
        mapDesc=msg.info;
        ROS_DEBUG("Received a %d X %d map @ %.3f m/pix  Origin X %.3f Y %.3f\n",
                msg.info.width,
                msg.info.height,
                msg.info.resolution,
                msg.info.origin.position.x,
                msg.info.origin.position.y);
    }
    
    /* we will start drawing squares using clicks*/
    void define_areas::clickCallback(const geometry_msgs::PointStamped::ConstPtr msg)
    {
        numberOfClicks=numberOfClicks+1 ;
        ROS_DEBUG("Clicked on %.2f, %.2f\n",msg->point.x,msg->point.y);
        if (numberOfClicks==0)
        {            
            startPoint=msg->point;            
        } 
        else if (numberOfClicks==1)
        {
            endPoint=msg->point;               
            ROS_DEBUG("  - name: \n    min:\n      x: %.2f\n      y: %.2f\n    max:\n      x: %.2f\n      y: %.2f\n\n",startPoint.x,startPoint.y,endPoint.x,endPoint.y);          
            drawSquare(startPoint.x,startPoint.y,endPoint.x,endPoint.y,1);
            publishMap();
            numberOfClicks=-1 ;
        }
            
        
    }
    
    
    void define_areas::publishMap()
    {
      
      map_.setTimestamp(ros::Time::now().toNSec());
      
      grid_map_msgs::GridMap message;
      grid_map::GridMapRosConverter::toMessage(map_, message);
      gridMapPublisher_.publish(message);
      ROS_DEBUG("Grid map (timestamp %f) published.", message.info.header.stamp.toSec());
    }


void define_areas::drawSquare(double start_x,double start_y,double end_x,double end_y,double value)
{
  //ROS_DEBUG("Drawing an square \n min:\nx: %.2f\ny: %.2f\n max:\nx: %.2f\ny: %.2f\n\n",start_x,start_y,end_x,end_y);
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


    
} // end of namespace define_areas




/* garbage
       areas[i].startX=1.39;
      areas[i].startY=-1.19;
      areas[i].endX=4.94;
      areas[i].endY=2.43;
      areas[i++].name="Kitchen";

      areas[i].startX=-6;
      areas[i].startY=-1.16;
      areas[i].endX=-0.48;
      areas[i].endY=2.15;
      areas[i++].name="Rest area";

      areas[i].startX=-6.01;
      areas[i].startY=2.07;
      areas[i].endX=-2.80;
      areas[i].endY=5.00;
      areas[i++].name="Entry";
      
      areas[i].startX=-2.88;
      areas[i].startY=2.37;
      areas[i].endX=4.1;
      areas[i].endY=4.9;
      areas[i++].name="Entry corridor";


      areas[i].startX=-0.26;
      areas[i].startY=-1.16;
      areas[i].endX=1.04;
      areas[i].endY=13.7;
      areas[i++].name="Long corridor";
 * */
