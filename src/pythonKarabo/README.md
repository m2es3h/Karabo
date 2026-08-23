# Karabo Python wheels

This directory contains the `karabo` Python distribution. The packaging changes in this branch support two related workflows:

1. The regular `pip` build now compiles the `karabind` pybind11 extension as part
   of the package build. A default build therefore contains the Python Karabo
   modules and the native bound API in the same wheel.
2. `cibuildwheel` can build release wheels containing `pythonKarabo`, the
   `karabind` extension, and the shared libraries required by that extension.

## Building the package

For a complete package, leave `BUILD_KARABO_SUBMODULE` unset and run the build
from this directory:

```bash
python -m pip install build
python -m build --wheel
```

`setup.py` uses pybind11.setup_helpers.Pybind11Extension to define sources, include and library paths and
builds the extension named `karabind`. It links the extension with the Karabo
C++ library and other shared library dependencies. The C++ dependencies and the Karabo library must be
available in the configured include and library paths; the cibuildwheel build
prepares those paths automatically.

The environment variable `BUILD_KARABO_SUBMODULE` is still available for the
smaller package variants used by other Karabo components:

- `NATIVE` packages the native-only Python subset and does not build `karabind`.
- `MDL` packages the middlelayer subset and does not build `karabind`.
- An unset value packages the complete distribution and builds `karabind`.

## Building with cibuildwheel

https://github.com/pypa/cibuildwheel

cibuildwheel is an open-source tool maintained by the Python Packaging Authority (PyPA) that automates building platform-specific Python wheels across Windows, macOS, Linux. When run locally, it pulls a standardized docker container and build karabo/karabind within it.  It then places compiled wheels in `wheelhouse/` off the project root.

To build wheels locally on your linux system, you need the ability to pull and run docker containers (distro dependent). Once that is setup, run:

```bash
pip install cibuildwheel  # in any python environment, any version
python -m cibuildwheel --config-file src/pythonKarabo/pyproject.toml
```

Before the wheel build, cibuildwheel runs the `before-all` commands from
`pyproject.toml` inside the cibuildwheel container. Those commands:

1. install the system development packages needed by the build;
2. install Conan and configure platform-provided dependencies;
3. install pinned Conan dependencies, including Boost, amqp-cpp,
   nlohmann-json, and spdlog;
4. configure and install the Karabo CMake targets into the container prefix.

This gives the setuptools extension build access to the headers and libraries
needed to compile `karabind` and link it against Karabo.

The build workflow that runs as a github action is defined in `.github/workflows/build.yml`. 

## How shared libraries enter the wheel

On Linux, cibuildwheel invokes `auditwheel` as its wheel-repair step. The
process is:

1. setuptools creates a normal wheel containing the Python package and the
   compiled `karabind` extension. At this point, the extension may refer to
   shared libraries outside the wheel, such as `libkarabo.so`.
2. `auditwheel repair` examines the ELF `DT_NEEDED` entries of the extension
   and follows the shared-library dependencies.
3. Libraries that are not allowed to remain external for the selected
   manylinux policy are copied into the wheel, normally in a platform-specific
   `.libs` directory. This includes the Karabo-built libraries and other
   non-system libraries available in the build prefix when they are required.
4. `auditwheel` rewrites the copied libraries' loader metadata and the
   extension's runtime search path so imports find the bundled files relative
   to the wheel. It also updates the wheel metadata and filename with the
   compatible manylinux tag.

The result is a wheel that can be installed without reproducing the Karabo
build environment or installing the Karabo C++ libraries separately. Standard platform
libraries that manylinux permits to remain external are not copied; the target
Linux system already provides these such as libc, libstdc++, libpthread, and similar.

```
(karabo-py312) user@host:~/Code/karabo-py312/lib/python3.12/site-packages$ ls -la
...
-rwxrwxr-x   1 user user 27650249 Aug 22 16:49 karabind.cpython-312-x86_64-linux-gnu.so
drwxrwxr-x  18 user user     4096 Aug 22 16:53 karabo
drwxrwxr-x   3 user user     4096 Aug 22 16:49 karabo-3.0.14.dev4+g3c03ef99e.d20260822.dist-info
drwxrwxr-x   2 user user     4096 Aug 22 16:49 karabo.libs
...
(karabo-py312) user@host:~/Code/karabo-py312/lib/python3.12/site-packages$ 
```

cibuildwheel automatically figures out karabind's shared library dependencies and puts them all in the karabo.libs directory.

```
(karabo-py312) user@host:~/Code/karabo-py312/lib/python3.12/site-packages$ ls -la karabo.libs/
total 44352
drwxrwxr-x   2 user user     4096 Aug 22 16:49 .
drwxrwxr-x 132 user user     4096 Aug 22 16:49 ..
-rwxrwxr-x   1 user user   965465 Aug 22 16:49 libamqpcpp-d61035ed.so.4.3
-rwxrwxr-x   1 user user   135913 Aug 22 16:49 libbrotlicommon-3fddcffd.so.1.0.6
-rwxrwxr-x   1 user user    66297 Aug 22 16:49 libbrotlidec-0a7ba021.so.1.0.6
-rwxrwxr-x   1 user user    21545 Aug 22 16:49 libcom_err-730ca923.so.2.1
-rwxrwxr-x   1 user user   140977 Aug 22 16:49 libcrypt-52aca757.so.1.1.0
-rwxrwxr-x   1 user user  3215921 Aug 22 16:49 libcrypto-a324fe28.so.1.1.1k
-rwxrwxr-x   1 user user   636377 Aug 22 16:49 libcurl-f8def1d0.so.4.5.0
-rwxrwxr-x   1 user user   186137 Aug 22 16:49 libfmt-df82586e.so.10.2.1
-rwxrwxr-x   1 user user   390897 Aug 22 16:49 libgssapi_krb5-abc338f9.so.2.2
-rwxrwxr-x   1 user user   144481 Aug 22 16:49 libidn2-2f4a5893.so.0.3.6
-rwxrwxr-x   1 user user   118289 Aug 22 16:49 libk5crypto-b242bd1e.so.3.1
-rwxrwxr-x   1 user user 32293345 Aug 22 16:49 libkarabo-02e3df91.so.3.0.13
-rwxrwxr-x   1 user user    17929 Aug 22 16:49 libkeyutils-2777d33d.so.1.6
-rwxrwxr-x   1 user user  1047617 Aug 22 16:49 libkrb5-d4b313c5.so.3.3
-rwxrwxr-x   1 user user    89265 Aug 22 16:49 libkrb5support-7177f7df.so.0.1
-rwxrwxr-x   1 user user    73361 Aug 22 16:49 liblber-2-d20824ef.4.so.2.10.9
-rwxrwxr-x   1 user user   377241 Aug 22 16:49 libldap-2-cea2a960.4.so.2.10.9
-rwxrwxr-x   1 user user   175025 Aug 22 16:49 libnghttp2-c45e57b9.so.14.17.0
-rwxrwxr-x   1 user user   547745 Aug 22 16:49 libpcre2-8-516f4c9d.so.0.7.1
-rwxrwxr-x   1 user user    82905 Aug 22 16:49 libpsl-99becdd3.so.5.3.1
-rwxrwxr-x   1 user user   274001 Aug 22 16:49 libpugixml-c8916052.so.1.13
-rwxrwxr-x   1 user user   142865 Aug 22 16:49 libsasl2-7de4d792.so.3.0.0
-rwxrwxr-x   1 user user   203297 Aug 22 16:49 libselinux-81bdf592.so.1
-rwxrwxr-x   1 user user   976041 Aug 22 16:49 libspdlog-8e9af468.so.1.14.1
-rwxrwxr-x   1 user user   516577 Aug 22 16:49 libssh-9f6d898c.so.4.8.7
-rwxrwxr-x   1 user user   687353 Aug 22 16:49 libssl-8248cfc9.so.1.1.1k
-rwxrwxr-x   1 user user  1826161 Aug 22 16:49 libunistring-05abdd40.so.2.1.0
(karabo-py312) user@host:~/Code/karabo-py312/lib/python3.12/site-packages$ 
```

cibuildwheel then ensures the RPATH of karabind and dependencies are all set properly.

```
(karabo-py312) user@host:~/Code/karabo-py312/lib/python3.12/site-packages$ readelf -d karabind.cpython-312-x86_64-linux-gnu.so 

Dynamic section at offset 0x1a44000 contains 32 entries:
  Tag        Type                         Name/Value
 0x000000000000000f (RPATH)              Library rpath: [$ORIGIN/karabo.libs]
 0x0000000000000001 (NEEDED)             Shared library: [libkarabo-02e3df91.so.3.0.13]
 0x0000000000000001 (NEEDED)             Shared library: [libssl-8248cfc9.so.1.1.1k]
 0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
 0x0000000000000001 (NEEDED)             Shared library: [libm.so.6]
 0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
 0x0000000000000001 (NEEDED)             Shared library: [libpthread.so.0]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 0x0000000000000001 (NEEDED)             Shared library: [ld-linux-x86-64.so.2]
 ...

(karabo-py312) user@host:~/Code/karabo-py312/lib/python3.12/site-packages$ ldd karabind.cpython-312-x86_64-linux-gnu.so 
	linux-vdso.so.1 (0x000078230105d000)
	libkarabo-02e3df91.so.3.0.13 => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libkarabo-02e3df91.so.3.0.13 (0x00007822fee00000)
	libssl-8248cfc9.so.1.1.1k => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libssl-8248cfc9.so.1.1.1k (0x00007822fea00000)
	libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007822fe600000)
	libm.so.6 => /usr/lib/x86_64-linux-gnu/libm.so.6 (0x00007823008da000)
	libgcc_s.so.1 => /usr/lib/x86_64-linux-gnu/libgcc_s.so.1 (0x0000782301017000)
	libpthread.so.0 => /usr/lib/x86_64-linux-gnu/libpthread.so.0 (0x0000782301010000)
	libc.so.6 => /usr/lib/x86_64-linux-gnu/libc.so.6 (0x00007822fe200000)
	/lib64/ld-linux-x86-64.so.2 (0x000078230105f000)
	libcurl-f8def1d0.so.4.5.0 => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libcurl-f8def1d0.so.4.5.0 (0x00007822fde00000)
	libamqpcpp-d61035ed.so.4.3 => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libamqpcpp-d61035ed.so.4.3 (0x00007822fed39000)
	libdl.so.2 => /usr/lib/x86_64-linux-gnu/libdl.so.2 (0x000078230100b000)
	libspdlog-8e9af468.so.1.14.1 => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libspdlog-8e9af468.so.1.14.1 (0x00007822fe937000)
	libfmt-df82586e.so.10.2.1 => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libfmt-df82586e.so.10.2.1 (0x0000782300fe0000)
	libpugixml-c8916052.so.1.13 => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libpugixml-c8916052.so.1.13 (0x00007822fda00000)
	libcrypto-a324fe28.so.1.1.1k => /home/user/Code/karabo-py312/lib/python3.12/site-packages/karabo.libs/libcrypto-a324fe28.so.1.1.1k (0x00007822fd400000)
	libz.so.1 => /usr/lib/x86_64-linux-gnu/libz.so.1 (0x0000782300fc2000)
    ...
```
