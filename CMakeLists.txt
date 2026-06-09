cmake_minimum_required(VERSION 3.8...3.22)
project(avular_simulations)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

include(GNUInstallDirs)

ament_python_install_package(${PROJECT_NAME}
  SKIP_COMPILE
  SCRIPTS_DESTINATION ${CMAKE_INSTALL_LIBDIR}/${PROJECT_NAME}
)

install(DIRECTORY launch DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROJECT_NAME})
install(DIRECTORY config DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROJECT_NAME})
install(DIRECTORY worlds DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROJECT_NAME})
install(DIRECTORY urdf DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROJECT_NAME})
install(DIRECTORY models DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROJECT_NAME})

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/gz_resources.dsv.in")
ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/gz_resources.sh.in")

ament_package()
