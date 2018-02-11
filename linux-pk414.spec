#
# Production LTS Kernel
#

Name:           linux-pk414
Version:        4.14.18
Release:        7
License:        GPL-2.0
Summary:        The Linux kernel
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.14.18.tar.xz
Source1:        config-pk414-sos
Source2:        config-pk414-standard
Source3:        cmdline-pk414-sos
Source4:        cmdline-pk414-standard

%define ktarget0 pk414-sos
%define kversion0 %{version}-%{release}.%{ktarget0}
%define ktarget1 pk414-standard
%define kversion1 %{version}-%{release}.%{ktarget1}

BuildRequires:  bash >= 2.03
BuildRequires:  bc
BuildRequires:  binutils-dev
BuildRequires:  elfutils-dev
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  kmod
BuildRequires:  linux-firmware
BuildRequires:  lz4

Requires: systemd-console
Requires: linux-pk414-sos
Requires: linux-pk414-standard

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

Patch0001: 0001-linux-pk414.patch

%description
The Linux kernel.

%package sos
License:        GPL-2.0
Summary:        The Linux kernel for Service OS
Group:          kernel

%description sos
The Linux kernel for Service OS

%package standard
License:        GPL-2.0
Summary:        The Linux kernel for Linux as a Guest
Group:          kernel

%description standard
The Linux kernel for Linux as a Guest

%package extra
License:        GPL-2.0
Summary:        The Linux kernel extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.14.18

%patch0001 -p1

cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
cp -a /usr/lib/firmware/i915 firmware/
cp -a /usr/lib/firmware/intel-ucode firmware/

%build
BuildKernel() {

    Target=$1
    Arch=x86_64
    ExtraVer="-%{release}.${Target}"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile
    perl -p -i -e "s/^CONFIG_LOCALVERSION=.*/CONFIG_LOCALVERSION=\"\"/" config-${Target}

    make O=${Target} -s mrproper
    cp config-${Target} ${Target}/.config

    make O=${Target} -s ARCH=${Arch} olddefconfig
    make O=${Target} -s ARCH=${Arch} CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} %{?sparse_mflags}
}

BuildKernel %{ktarget0}
BuildKernel %{ktarget1}

%install

InstallKernel() {

    Target=$1
    Kversion=$2
    Arch=x86_64
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 ${Target}/.config    ${KernelDir}/config-${Kversion}
    install -m 644 ${Target}/System.map ${KernelDir}/System.map-${Kversion}
    install -m 644 ${Target}/vmlinux    ${KernelDir}/vmlinux-${Kversion}
    install -m 644 cmdline-${Target}    ${KernelDir}/cmdline-${Kversion}
    cp  ${Target}/arch/x86/boot/bzImage ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules
    make O=${Target} -s ARCH=${Arch} INSTALL_MOD_PATH=%{buildroot}/usr modules_install

    rm -f %{buildroot}/usr/lib/modules/${Kversion}/build
    rm -f %{buildroot}/usr/lib/modules/${Kversion}/source

    ln -s org.clearlinux.${Target}.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-${Target}
}

InstallKernel %{ktarget0} %{kversion0}
InstallKernel %{ktarget1} %{kversion1}

rm -rf %{buildroot}/usr/lib/firmware

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion0}
%dir /usr/lib/modules/%{kversion1}

%files sos
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion0}
/usr/lib/kernel/config-%{kversion0}
/usr/lib/kernel/cmdline-%{kversion0}
/usr/lib/kernel/org.clearlinux.%{ktarget0}.%{version}-%{release}
/usr/lib/kernel/default-%{ktarget0}
/usr/lib/modules/%{kversion0}/kernel
/usr/lib/modules/%{kversion0}/modules.*

%files standard
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion1}
/usr/lib/kernel/config-%{kversion1}
/usr/lib/kernel/cmdline-%{kversion1}
/usr/lib/kernel/org.clearlinux.%{ktarget1}.%{version}-%{release}
/usr/lib/kernel/default-%{ktarget1}
/usr/lib/modules/%{kversion1}/kernel
/usr/lib/modules/%{kversion1}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion0}
/usr/lib/kernel/System.map-%{kversion1}
/usr/lib/kernel/vmlinux-%{kversion0}
/usr/lib/kernel/vmlinux-%{kversion1}
