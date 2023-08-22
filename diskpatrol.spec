Name:           diskpatrol
Version:        0.0.1
Release:        1%{?dist}
Summary:        A diskpatrol program

License:        GPL
Source0:        %{name}-%{version}.tar.gz

%description
A Disk Patrol Application


%prep
%autosetup


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/systemd/system
cp %{name} $RPM_BUILD_ROOT/%{_bindir}
cp %{name}.conf $RPM_BUILD_ROOT/%{_sysconfdir}
cp %{name}.service $RPM_BUILD_ROOT/%{_sysconfdir}/systemd/system

%files
%{_bindir}/%{name}
%{_sysconfdir}/%{name}.conf
%{_sysconfdir}/systemd/system/%{name}.service

%changelog
* Tue Aug 22 2023 Heechul Kim <jijisa@iorchard.net>
- 
