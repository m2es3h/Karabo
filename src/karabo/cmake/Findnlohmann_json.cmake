# look for the header file in standard system paths (like /usr/include)
find_path(nlohmann_json_INCLUDE_DIR
    NAMES nlohmann/json.hpp
)

# handle REQUIRED/QUIET arguments and set nlohmann_json_FOUND
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(nlohmann_json
    REQUIRED_VARS nlohmann_json_INCLUDE_DIR
)

# create an exported target
if(nlohmann_json_FOUND AND NOT TARGET nlohmann_json::nlohmann_json)
    add_library(nlohmann_json::nlohmann_json INTERFACE IMPORTED GLOBAL)
    set_target_properties(nlohmann_json::nlohmann_json  PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${nlohmann_json_INCLUDE_DIR}"
    )
endif()
