# look for the header file in standard system paths (like /usr/include)
find_path(spdlog_INCLUDE_DIR
    NAMES spdlog/spdlog.h
)

# look for the library binary file in standard system paths (like /usr/lib)
find_library(spdlog_LIBRARY
    NAMES spdlog
)

# handle REQUIRED/QUIET arguments and set spdlog_FOUND
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(spdlog
    REQUIRED_VARS spdlog_LIBRARY spdlog_INCLUDE_DIR
)

# create an exported target
if(spdlog_FOUND AND NOT TARGET spdlog::spdlog)
    add_library(spdlog::spdlog UNKNOWN IMPORTED GLOBAL)
    set_target_properties(spdlog::spdlog PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${spdlog_INCLUDE_DIR}"
        IMPORTED_LOCATION "${spdlog_LIBRARY}"
    )
endif()
