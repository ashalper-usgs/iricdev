Name:           iric
Version:        0.1
Release:        1%{?dist}
Summary:        A river flow and riverbed variation analysis software package.

License:        BSD
URL:            http://i-ric.org/en/introduction/
Source0:        https://github.com/ashalper-usgs/iricdev/archive/master.zip

BuildRequires:  make, coreutils, hdf5-devel

%description
iRICXXX (International River Interface Cooperative) is a river flow
and riverbed variation analysis software package which combines the
functionality of MD_SWMS, developed by the USGS (U.S. Geological
Survey) and RIC-Nays, developed by the Foundation of Hokkaido River
Disaster Prevention Research Center.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q -n iricdev-master
rm -rf master/external
mkdir -p master/external

cp /root/Fastmech-BMI/bin/create-paths-pri-solver.sh .
cp /root/Fastmech-BMI/bin/create-dirExt-prop-solver.sh .

. ./versions.sh

if [ ! -f "%{_tmppath}/cgnslib_${CGNSLIB_VER}.tar.gz" ]; then
  wget --no-check-certificate \
      -O %{_tmppath}/cgnslib_${CGNSLIB_VER}.tar.gz \
      https://downloads.sourceforge.net/project/cgns/cgnslib_3.2/cgnslib_${CGNSLIB_VER}.tar.gz
fi
cp %{_tmppath}/cgnslib_${CGNSLIB_VER}.tar.gz .

if [ ! -f "%{_tmppath}/iriclib-${IRICLIB_VER:0:7}.zip" ]; then
  wget --no-check-certificate -O "%{_tmppath}/iriclib-${IRICLIB_VER:0:7}.zip" \
      https://github.com/i-RIC/iriclib/archive/${IRICLIB_VER}.zip
fi
cp %{_tmppath}/iriclib-${IRICLIB_VER:0:7}.zip .


%build
# TODO: not sure if this is necessary in this section
. ./versions.sh

# begin Fastmech-BMI/bin/build-gcc-solver.sh
GENERATOR="Unix Makefiles"
SGEN="gcc"

export GENERATOR SGEN

# begin iricdev/build-cgnslib.sh
. ./versions.sh
VER=$CGNSLIB_VER

rm -rf lib/src/cgnslib-$VER
rm -rf lib/build/cgnslib-$VER
rm -rf lib/install/cgnslib-$VER

mkdir -p lib/src
cd lib/src
tar xvzf ../../cgnslib_$VER.tar.gz
mv cgnslib_$VER cgnslib-$VER
cd ../..

#ctest -S build-cgnslib.cmake -DCONF_DIR:STRING=debug   "-DCTEST_CMAKE_GENERATOR:STRING=${GENERATOR}" -C Debug   -VV -O ${SGEN}-cgnslib-debug.log
ctest -S build-cgnslib.cmake -DCONF_DIR:STRING=release \
    "-DCTEST_CMAKE_GENERATOR:STRING=${GENERATOR}" -C Release -VV \
    -O ${SGEN}-cgnslib-release.log
# end build-cgnslib.sh

./build-iriclib.sh

./create-paths-pri-solver.sh > paths.pri
./create-dirExt-prop-solver.sh > dirExt.prop

# end iricdev/build-cgnslib.sh

%install
rm -rf $RPM_BUILD_ROOT

# TODO: might not be the appropriate section for this
for lib in `ls -1 lib/install`; do
    echo "- $lib"
    if [ -d lib/install/$lib/release ]; then
    	lib_src_dir=lib/install/$lib/release
    else
    	lib_src_dir=lib/install/$lib
    fi
    cp -R $lib_src_dir/* master/external
done

install -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_includedir}
install lib/install/iriclib-a6a110f/release/lib/libiriclib.so $RPM_BUILD_ROOT%{_libdir}
install lib/install/iriclib-a6a110f/release/include/*iric*.h $RPM_BUILD_ROOT%{_includedir}
find -type f -and -name '*iric*' -and -not -name '*iric*.*o*'
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc
%{_libdir}/*.so

%files devel
%doc
%{_includedir}/*
#%{_libdir}/*.so


%changelog
* Mon Dec 10 2018 Andrew Halper <ashalper@usgs.gov> - 0.1-1
- Built on CentOS 7.
