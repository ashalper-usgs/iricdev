Name:           iric
Version:        0.1
Release:        1%{?dist}
Summary:        A river flow and riverbed variation analysis software package.

License:        BSD
URL:            http://i-ric.org/en/introduction/
Source0:        https://github.com/ashalper-usgs/iricdev/archive/master.zip

BuildRequires:  make, coreutils

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
%setup -q -n master


%build
# TODO


%install
rm -rf $RPM_BUILD_ROOT
# Build the iricdev library used by Fastmech. The install directory
# for the libraries is passed as an argument.
dst_dir=`pwd`/external
if [ -d $dst_dir ]; then
    echo "Destination ($dst_dir) exists -- done"
    exit 0
else
    mkdir -p $dst_dir
fi

src_dir=$PWD/lib/install
cp /root/Fastmech-BMI/bin/build-gcc-solver.sh .
cp /root/Fastmech-BMI/bin/create-paths-pri-solver.sh .
cp /root/Fastmech-BMI/bin/create-dirExt-prop-solver.sh .

. ./versions.sh

# if SZip/Zlib/hdf5 source is not cached
if [ ! -f "%{_tmppath}/hdf5-${HDF5_VER}.tar.gz" ]; then
    # get it
    MAJOR=$(echo ${HDF5_VER} | cut -d '.' -f 1)
    MINOR=$(echo ${HDF5_VER} | cut -d '.' -f 2)
    wget --no-check-certificate -O %{_tmppath}/SZip.tar.gz \
	https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-${MAJOR}.${MINOR}/hdf5-${HDF5_VER}/cmake/SZip.tar.gz
    wget --no-check-certificate -O %{_tmppath}/ZLib.tar.gz \
	https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-${MAJOR}.${MINOR}/hdf5-${HDF5_VER}/cmake/ZLib.tar.gz
    wget --no-check-certificate -O %{_tmppath}/hdf5-${HDF5_VER}.tar.gz \
	https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-${MAJOR}.${MINOR}/hdf5-${HDF5_VER}/src/hdf5-${HDF5_VER}.tar.gz
fi
cp %{_tmppath}/SZip.tar.gz %{_tmppath}/ZLib.tar.gz \
    %{_tmppath}/hdf5-${HDF5_VER}.tar.gz .

if [ ! -f "%{_tmppath}/cgnslib_${CGNSLIB_VER}.tar.gz" ]; then
  wget --no-check-certificate \
      -O %{_tmppath}/cgnslib_${CGNSLIB_VER}.tar.gz \
      https://downloads.sourceforge.net/project/cgns/cgnslib_3.2/cgnslib_${CGNSLIB_VER}.tar.gz
fi
cp %{_tmppath}/cgnslib_${CGNSLIB_VER}.tar.gz .

if [ ! -f "%{_tmppath}/iriclib-${IRICLIB_VER:0:7}.zip" ]; then
  wget --no-check-certificate -O iriclib-${IRICLIB_VER:0:7}.zip \
      https://github.com/i-RIC/iriclib/archive/${IRICLIB_VER}.zip
fi
cp %{_tmppath}/iriclib-${IRICLIB_VER:0:7}.zip .

./build-gcc-solver.sh

echo "src: $src_dir"
echo "dst: $dst_dir"
for lib in `ls -1 $src_dir`; do
    echo "- $lib"
    if [ -d $src_dir/$lib/release ]; then
    	lib_src_dir=$src_dir/$lib/release
    else
    	lib_src_dir=$src_dir/$lib
    fi
    cp -R $lib_src_dir/* $dst_dir
done

install -d $RPM_BUILD_ROOT
find %{_topdir} -name '*.so*'

# TODO:
#find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc
#%{_libdir}/*.so.*

%files devel
%doc
#%{_includedir}/*
#%{_libdir}/*.so


%changelog
* Tue Dec 4 2018 Andrew Halper <ashalper@usgs.gov> - 0.1-1
- Built on CentOS.
