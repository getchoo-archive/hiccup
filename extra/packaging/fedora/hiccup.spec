%global commit 22378abce34f4b27db884692d5d99bec9dcef034
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           hiccup
Version:        %{shortcommit}
Release:        1%{?dist}
Summary:        a python script to help keep you up to date 

License:        MIT
URL:            https://github.com/getchoo/hiccup
Source0:        %{URL}/archive/%{commit}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
a python script that attempts to upgrade your system with multiple package managers.}

%description %_description


%prep
%autosetup -n %{name}-%{commit}


%generate_buildrequires
%pyproject_buildrequires -w


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files hiccup


%check
%pyproject_check_import


%files -f %{pyproject_files}
%doc README.md docs/default-config.json
%{_bindir}/%{name}


%changelog
* Fri Aug 26 2022 seth <getchoo@tuta.io>
-  initial commit 
