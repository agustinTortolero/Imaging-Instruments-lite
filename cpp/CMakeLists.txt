cmake_minimum_required(VERSION 3.10)

# Project name
project(ImageProcessor LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find OpenMP
find_package(OpenMP REQUIRED)

# Add source files
set(SOURCES
    cpu_image_processor.cpp
)

# Add header files (optional, for IDEs)
set(HEADERS
    cpu_image_processor.h
)

# Create the shared library with a custom output name
add_library(cpu_filtering SHARED ${SOURCES})

# Link OpenMP
target_link_libraries(cpu_filtering PRIVATE OpenMP::OpenMP_CXX)

# Include directories
target_include_directories(cpu_filtering PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Set output library name
set_target_properties(cpu_filtering PROPERTIES OUTPUT_NAME "cpu_filtering")

