# look for the header file in standard system paths (like /usr/include)
find_path(amqpcpp_INCLUDE_DIR
    NAMES amqpcpp.h
)

# look for the library binary file in standard system paths (like /usr/lib)
find_library(amqpcpp_LIBRARY
    NAMES amqpcpp
)

# handle REQUIRED/QUIET arguments and set amqpcpp_FOUND
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(amqpcpp
    REQUIRED_VARS amqpcpp_LIBRARY amqpcpp_INCLUDE_DIR
)

# create an exported target
if(amqpcpp_FOUND AND NOT TARGET amqpcpp)
    add_library(amqpcpp UNKNOWN IMPORTED GLOBAL)
    set_target_properties(amqpcpp PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${amqpcpp_INCLUDE_DIR}"
        IMPORTED_LOCATION "${amqpcpp_LIBRARY}"
    )
endif()
