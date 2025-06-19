cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

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
