#!/bin/bash

err() {
	printf "\n%s\n" "$2" >&2
	exit $1
}

output() {
	printf "${BOLD}%s${UNBOLD}\n" "$@"
}

addtolog() {
	[ -f $LOGFILE ] && mv $LOGFILE ${LOGFILE%.*}.$(ls -l ${LOGFILE%.*}*.log | wc -l | awk '{ print $1 }').log
	echo $@ >> $LOGFILE
}

donwload_source() {
	local OLD_PWD=$PWD
	cd $srcdir/

	if [[ $source =~ "git://" ]]; then
		download_manager="git clone"
	else
		download_manager="curl -JLO"
	fi


	if [ ! -z $md5sums ]; then
		local csum=("${md5sums[@]}")
		local csum_prg="md5"
	elif [ ! -z $sha1sums ]; then
		local csum=("${sha1sums[@]}")
		local csum_prg="shasum"
	elif [ ! -z $sha256sums ]; then
		local csum=("${sha256sums[@]}")
		local csum_prg="shasum -a 256"
	elif [ ! -z $sha384sums ]; then
		local csum=("${sha384sums[@]}")
		local csum_prg="shasum -a 384"
	elif [ ! -z $sha512sums ]; then
		local csum=("${sha512sums[@]}")
		csum_prg="shasum -a 512"
	else
		err 10 "Unknown checksum"
	fi

	local i=0
	for s in $source; do
		output "[ Downloading ] $s"
		$download_manager $s
		filename="$(ls -lat | head -2 | tail -1 | awk '{ print $9 }')"
		echo "${csum[i]}  $filename" | $csum_prg -c -s -
		[ $? -ne 0 ] && err 11 "Checksum failed" || output "[ Checksum ] Checksum correct"
		let i=$i+1
	done

	cd $OLD_PWD
	printf "\n\n"
}

generate_control() {
	printf "Package: %s\n" $pkgname
	printf "Version: %s\n" "$([ -z $pkgrel ] && echo $pkgver || echo $pkgver-$pkgrel)"
	local aarch=$(IFS=' '; echo "${arch[*]}")

	# Replace 'any' entry from Arch PKGBUILD with 'all'
	printf "Architecture: %s\n"	"${aarch/any/all}"

	printf "Maintainer: %s\n" $MAINTAINER
	printf "Description: %s\n" "$pkgdesc"

	local deps=$(IFS=,\ ; echo "${depends[*]}")
	printf "Depends: %s\n" $deps
	printf "Homepage: %s\n" "$url"
	
	addtolog "Dependencies: $deps"
}

install_makedeps() {

	makedeps_toinstall=()
	for p in $makedepends; do
		dpkg-query -s $p &>/dev/null || makedeps_toinstall+=$p
	done

	[ ${#makedeps_toinstall[@]} -eq 0 ] && return 0
	read -p "This package needs as makedepends the following dependencies: ${makedepends[*]}.
You need to install: ${makedeps_toinstall[*]}

Do you want to install them? [Y/n] " -n 1 ch

	[ "$ch" = 'n' -o "$ch" = 'N' ] && err 3 "Dependencies unsatisfied."

	$su_agent apt-get install -y $makedeps_toinstall
	printf "\n\n"
	return $?
}

# Setting up basic variables
[ $UID -eq 0 ] && err 1 "You cannot execute makedebpkg as root."
[ -z $PWD ] && PWD=$(pwd)
[ -z $MAINTAINER ] && MAINTAINER=$USER
BOLD='\033[1m'
UNBOLD='\033[0m'

PKGBUILD_PATH=$PWD/PKGBUILD
LOGFILE=$PWD/makedebpkg.log

# Setting up options
while getopts hcf: opt; do
	case $opt in
		"h")
			printf "Usage: $(basename $0) [-h] [-c] [-f file]\n"
			exit 0
			;;
		"c")
			rm -rf $PWD/srcdir
			;;
		"f")
			PKGBUILD_PATH=$OPTARG
			;;
	esac
done
shift "$((OPTIND - 1))"


# if PKGBUILD doesn't exists, then stop everything
[ -e $PKGBUILD_PATH ] || err 2 "\"PKGBUILD\" file not found."


[ -e /usr/bin/which ] && if which sudo &>/dev/null; then
	su_agent="sudo"
else
	sufn() {
		su -c "$@"
	}
	su_agent=sufn
fi

# Getting PKGBUILD info
source $PKGBUILD_PATH

# Installing makedepends
install_makedeps || err 3 "Failed to install dependencies."

# Setting up build environment
export srcdir=$PWD/srcdir
export pkgdir=$PWD/$pkgname-$([ -z $pkgrel ] && echo $pkgver || echo $pkgver-$pkgrel)

mkdir -p $pkgdir/DEBIAN/
mkdir -p $srcdir/

# Donwloading source
donwload_source

generate_control > $pkgdir/DEBIAN/control

declare -f -F build &>/dev/null && build
declare -f -F package &>/dev/null && package

# Build deb package
dpkg-deb -b $pkgdir || err 12 "Failed to build package" 

# Uninstalling makedepends
[ ${#makedeps_toinstall[@]} -eq 0 ] || $su_agent apt-get purge -y $makedeps_toinstall

printf "\n${BOLD}Package: %s${UNBOLD} ready.\n" "$pkgname-$([ -z $pkgrel ] && echo $pkgver || echo $pkgver-$pkgrel)"