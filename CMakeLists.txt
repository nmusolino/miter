cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Python 3.12
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

find_package(nanobind CONFIG REQUIRED)


nanobind_add_module(
  _core
  STABLE_ABI  # Target Stable ABI for Python 3.12+
  NB_STATIC   # Build libnanobind statically
  # Sources
  src/main.cpp
)
install(TARGETS _core LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME})

if (PROJECT_IS_TOP_LEVEL)
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E create_symlink
            ${CMAKE_BINARY_DIR}/compile_commands.json
            ${CMAKE_CURRENT_SOURCE_DIR}/build/compile_commands.json
    )
endif()
