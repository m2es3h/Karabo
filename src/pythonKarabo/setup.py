# This file is part of Karabo.
#
# http://www.karabo.eu
#
# Copyright (C) European XFEL GmbH Schenefeld. All rights reserved.
#
# Karabo is free software: you can redistribute it and/or modify it under
# the terms of the MPL-2 Mozilla Public License.
#
# You should have received a copy of the MPL-2 Public License along with
# Karabo. If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.
#
# Karabo is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# flake8: noqa

import os
import sys
from pathlib import Path
from site import getsitepackages  #, getusersitepackages
from glob import glob

from pybind11.setup_helpers import Pybind11Extension, ParallelCompile, naive_recompile
from setuptools import find_packages, setup

# avoid re-compiling C++ source files that have not changed
# comment this line out to force a recompile of all header and source files
#ParallelCompile("NUM_JOBS", needs_recompile=naive_recompile).install()

# get path to karabo extern directory
compiletime_dirs = [Path(pkg).parent.parent.parent for pkg in getsitepackages()]
# use compile-time arguments same as karabind's CMakeLists.txt
extra_compile_args = [
    '-DBOOST_ALL_DYN_LINK',
    '-DFMT_SHARED',
    '-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION',
    '-DSPDLOG_COMPILED_LIB',
    '-DSPDLOG_FMT_EXTERNAL',
    '-DUSE_OS_TZDB=0',
    '-D__SO__',
    '-flto=auto',
    '-fno-fat-lto-objects',
    '-fvisibility=hidden',
    '-Wfatal-errors',
    '-Wno-unused-local-typedefs',
    '-Wno-noexcept-type',
    '-Wall',
    '-Wno-deprecated-declarations'] if sys.platform.startswith("linux") else []

karabo_dirs = [pkg.parent for pkg in compiletime_dirs]
karabind_dir = Path(__file__).resolve().parent.parent / 'karabind'

if sys.platform == "darwin":
    runtime_dirs = ["@loader_path/../../karabo/", "@loader_path/../../../", "@loader_path/../../../../", *getsitepackages()]
else:
    runtime_dirs = ["$ORIGIN/../../karabo/", "$ORIGIN/../../../", "$ORIGIN/../../../../", *getsitepackages()]

SUBMODULE = os.getenv("BUILD_KARABO_SUBMODULE", "")
print(f"Building karabo submodule: '{SUBMODULE}'")

install_args = {
    "name": "karabo",
    "author": "Karabo Team",
    "author_email": "opensource@xfel.eu",
    "description": "This is the Python interface of the Karabo control system",
    "url": "http://karabo.eu",
    "license": "MPL2",
}

if SUBMODULE == "NATIVE":
    # We"re building the GUI, so we don"t need to package everything
    install_args["packages"] = find_packages(include=[
        "karabo", "karabo.common*", "karabo.native*", "karabo.testing*"
])
    install_args["package_data"] = {
        "karabo.common.scenemodel.tests": [
            "data/*.svg", "data/inkscape/*.svg", "data/legacy/*.svg",
            "data/legacy/icon_data/*.svg"
        ],
        "karabo.testing": ["resources/*.*"],
    }

elif SUBMODULE == "MDL":
    install_args["packages"] = find_packages(include=[
        "karabo", "karabo.common*", "karabo.native*", "karabo.testing*",
        "karabo.interactive*", "karabo.middlelayer*",
        "karabo.middlelayer_devices*",
        "karabo.packaging*",
    ])
    install_args["package_data"] = {
        "karabo.common.scenemodel.tests": [
            "data/*.svg", "data/inkscape/*.svg", "data/legacy/*.svg",
            "data/legacy/icon_data/*.svg"
        ],
        "karabo.middlelayer.tests": ["*.xml"],
        "karabo.testing": ["resources/*.*"],
    }
    install_args["entry_points"] = {
        "console_scripts": [
            "karabo=karabo.interactive.karabo:main",
            "karabo-middlelayerserver=karabo.middlelayer.device_server:MiddleLayerDeviceServer.main",
            "ikarabo=karabo.interactive.ikarabo:main",
        ],
        "karabo.middlelayer_device": [
            "PropertyTest=karabo.middlelayer_devices.property_test:PropertyTest",
        ],
    }

else:
    # When building karabo, everything gets included
    install_args["packages"] = find_packages()
    install_args["package_data"] = {
        "karabo.bound.tests": ["resources/*.*"],
        "karabo.common.scenemodel.tests": [
            "data/*.svg", "data/inkscape/*.svg", "data/legacy/*.svg",
            "data/legacy/icon_data/*.svg"
        ],
        "karabo.middlelayer.tests": ["*.xml"],
        "karabo.project_db": ["config_stubs/*.*"],
        "karabo.interactive": [
            "static/*.css",
            "static/*.js",
            "static/*.html",
            "static/favicon.ico",
            "templates/*.html",
            "tests/karaboDB"],
        "karabo.testing": ["resources/*.*"],
        "karabo.influx_db.tests": ["sample_data/PropertyTestDevice/raw/*.txt"],
    }

    install_args["entry_points"] = {
        "console_scripts": [
            "karabo=karabo.interactive.karabo:main",
            "karabo-pythonserver=karabo.bound.device_server:main",
            "karabo-middlelayerserver=karabo.middlelayer.device_server:DeviceServer.main",
            "karabo-macroserver=karabo.middlelayer.macro_server:MacroServer.main",
            "karabo-cli=karabo.interactive.ideviceclient:main",
            "ikarabo=karabo.interactive.ikarabo:main",
            "convert-karabo-device=karabo.interactive.convert_device_project:main",
            "migrate-configdb=karabo.interactive.convert_config_db:main",
            "karabo-scene2cpp=karabo.interactive.scene2cpp:main",
            "karabo-scene2py=karabo.interactive.scene2python:main",
            "karabo-start=karabo.interactive.startkarabo:startkarabo",
            "karabo-stop=karabo.interactive.startkarabo:stopkarabo",
            "karabo-kill=karabo.interactive.startkarabo:killkarabo",
            "karabo-check=karabo.interactive.startkarabo:checkkarabo",
            "karabo-gterm=karabo.interactive.startkarabo:gnometermlog",
            "karabo-xterm=karabo.interactive.startkarabo:xtermlog",
            "karabo-less=karabo.interactive.startkarabo:less",
            "karabo-add-deviceserver=karabo.interactive.startkarabo:adddeviceserver",
            "karabo-remove-deviceserver=karabo.interactive.startkarabo:removedeviceserver",
            "karabo-create-services=karabo.interactive.startkarabo:make_service_dir",
            "karabo-webserver=karabo.interactive.webserver:run_webserver",
            "karabo-webaggregatorserver=karabo.interactive.webaggregatorserver:run_webserver",
            "migrate-karabo-history=karabo.influx_db.dl_migrator:main",
            "karabo-check-container=karabo.interactive.container_monitor:main",
        ],
        "karabo.bound_device": [
            "PropertyTest=karabo.bound_devices.property_test:PropertyTest",
        ],
        "karabo.middlelayer_device": [
            "PropertyTest=karabo.middlelayer_devices.property_test:PropertyTest",
            "ProjectManager=karabo.middlelayer_devices.project_manager:ProjectManager",
            "ConfigurationManager=karabo.middlelayer_devices.configuration_manager:ConfigurationManager",
            "DaemonManager=karabo.middlelayer_devices.daemon_manager:DaemonManager",
        ],
        "karabo.middlelayer_device_test": [
            "MiddlelayerDevice=karabo.integration_tests.device_cross_test.test_cross:MiddlelayerDevice",
            "MdlOrderTestDevice=karabo.integration_tests.signal_slot_order_test.mdl_ordertest_device:MdlOrderTestDevice",
            "SimpleTopology=karabo.integration_tests.mdl_client_test.device_simple:SimpleTopology",
        ],
        "karabo.macro_device": [
            "MetaMacro=karabo.middlelayer.metamacro:MetaMacro"
        ],
        "karabo.bound_device_test": [
            "TestDevice=karabo.bound.tests.boundDevice:TestDevice",
            "CommTestDevice=karabo.integration_tests.device_comm_test.commtestdevice:CommTestDevice",
            "SceneProvidingDevice=karabo.integration_tests.device_provided_scenes_test.scene_providing_device:SceneProvidingDevice",
            "NonSceneProvidingDevice=karabo.integration_tests.device_provided_scenes_test.non_scene_providing_device:NonSceneProvidingDevice",
            "DeviceWithLimit=karabo.integration_tests.device_schema_injection_test.device_with_limit:DeviceWithLimit",
            "DeviceWithTableElementParam=karabo.integration_tests.device_schema_injection_test.device_with_table_parameter:DeviceWithTableElementParam",
            "DeviceChannelInjection=karabo.integration_tests.device_schema_injection_test.device_channel_injection:DeviceChannelInjection",
            "PPSenderDevice=karabo.integration_tests.pipeline_processing_test.ppsender:PPSenderDevice",
            "PPReceiverDevice=karabo.integration_tests.pipeline_processing_test.ppreceiver:PPReceiverDevice",
            "UnstoppedThreadDevice=karabo.integration_tests.device_comm_test.unstoppedThreadDevice:UnstoppedThreadDevice",
            "SlowStartDevice=karabo.integration_tests.device_comm_test.slowStartDevice:SlowStartDevice",
            "StuckLoggerDevice=karabo.integration_tests.device_comm_test.stuckLoggerDevice:StuckLoggerDevice",
            "RaiseInitializationDevice=karabo.integration_tests.device_comm_test.raiseInitializationDevice:RaiseInitializationDevice",
            "RaiseOnDunderInitDevice=karabo.integration_tests.device_comm_test.raiseInitializationDevice:RaiseOnDunderInitDevice",
            "InvalidImportDevice=karabo.integration_tests.device_comm_test.invalidImportDevice:InvalidImportDevice",
            "SignalDevice=karabo.integration_tests.device_comm_test.signalCarryingDevice:SignalDevice",
            "BoundOrderTestDevice=karabo.integration_tests.signal_slot_order_test.bound_ordertest_device:BoundOrderTestDevice",
        ],
        "karabo.bound_broken_device_test": [
            "BrokenTestDevice=karabo.bound.tests.brokenBoundDevice:BrokenTestDevice",
        ],
    }

    install_args['ext_modules'] = [
        Pybind11Extension(
            name = 'karabind',
            sources = [
                *sorted(glob("../karabind/*.cc")),
            ],
            extra_compile_args=extra_compile_args,
            include_dirs=[
                *[str(Path(extern_dir) / "include") for extern_dir in compiletime_dirs],
                # path to this project's src directory
                *[str(d / "include") for d in karabo_dirs],
                str(karabind_dir),
            ],
            library_dirs=[
                *[str(Path(extern_dir) / "lib") for extern_dir in compiletime_dirs],
                *[str(d / "lib") for d in karabo_dirs],
            ],
            runtime_library_dirs=[
                *[str(Path(base_dir) / "lib") for base_dir in runtime_dirs],
            ],
            libraries=["karabo", "ssl"],
            language='c++',
            cxx_std=20,
        ),
    ]


if __name__ == "__main__":
    setup(**install_args)
