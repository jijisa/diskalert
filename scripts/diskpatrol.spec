Name:           diskpatrol
Version:        %%VERSION%%
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
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
cp %{name} $RPM_BUILD_ROOT/%{_bindir}
[ ! -f $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}.conf ] && \
    cp %{name}.conf $RPM_BUILD_ROOT/%{_sysconfdir} || :
cp %{name}.service $RPM_BUILD_ROOT/%{_sysconfdir}/systemd/system
cp %{name}.logrotate $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/%{name}

%files
%{_bindir}/%{name}
%{_sysconfdir}/%{name}.conf
%{_sysconfdir}/systemd/system/%{name}.service
%{_sysconfdir}/logrotate.d/%{name}

%config(noreplace) %{_sysconfdir}/%{name}.conf

%post
chmod 0640 %{_sysconfdir}/%{name}.conf

%changelog
* Tue Aug 22 2023 Heechul Kim <jijisa@iorchard.net>
- 
