cmake_minimum_required(VERSION 2.8.3)
project(rfid_sensor_layer)

find_package(catkin REQUIRED COMPONENTS
  angles
  roscpp
  costmap_2d
  sensor_msgs
  rfid_node
  pluginlib)

generate_dynamic_reconfigure_options(cfg/RFIDSensorLayer.cfg)

catkin_package(
CATKIN_DEPENDS sensor_msgs rfid_node
)

include_directories(include ${catkin_INCLUDE_DIRS})

add_library(${PROJECT_NAME} src/rfid_sensor_layer.cpp)
add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}_gencfg)
add_dependencies(${PROJECT_NAME} rfid_node_generate_messages_cpp)

target_link_libraries(${PROJECT_NAME} ${catkin_LIBRARIES})

install(TARGETS rfid_sensor_layer
        LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
        )

install(FILES costmap_plugins.xml
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
    )

install(PROGRAMS scripts/send_message.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
  
