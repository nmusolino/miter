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

if (CMAKE_EXPORT_COMPILE_COMMANDS AND MITER_COMPILE_COMMANDS_DIR)
    # Copy compile_commands.json to user-specified directory.
    add_custom_target(copy-compile-commands ALL
        ${CMAKE_COMMAND} -E copy_if_different
            ${CMAKE_BINARY_DIR}/compile_commands.json ${MITER_COMPILE_COMMANDS_DIR}
    )
endif()
