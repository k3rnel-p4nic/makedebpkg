#!/usr/bin/env python3
# -*- coding: latin-1 -*-
#
#	Copyright (c) 2018
#	Angelone Alessandro <angelone.alessandro98@gmail.com>.
# 	All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.


from argparse import ArgumentParser
from os.path import realpath, dirname, isdir
from sys import stderr
from os import getuid, getcwd, mkdir, environ
from tarfile import open as tar_open
from zipfile import ZipFile
from subprocess import run as run_cmd

from pkgdownload import PkgDownloadManager
from pkgdata import PkgData
from control import ControlData


def expand_vars(pkgdata: PkgData, srcdir, pkgdir):
	"""Expand Bash variables in strings, using PKGBUILD basic variables"""
	if not isinstance(pkgdata, PkgData):
		raise TypeError("Invalid type for pkgdata.")
		

	def replace_vars(s, pkgdata):
		if s.find('${pkgver}') >= 0:
		 	s = s.replace('${pkgver}', pkgdata.pkgver)

		if s.find('${pkgname}') >= 0:
		 	s = s.replace('${pkgname}', pkgdata.pkgname)

		if s.find('${pkgrel}') >= 0:
		 	s = s.replace('${pkgrel}', pkgdata.pkgrel)

		if s.find('${epoch}') >= 0:
		 	s = s.replace('${epoch}', pkgdata.epoch)

		if s.find('${arch}') >= 0:
		 	s = s.replace('${arch}', pkgdata.arch)

		if s.find('$pkgname') >= 0:
			s = s.replace('$pkgname', pkgdata.pkgname)

		if s.find('$pkgver') >= 0:
			s = s.replace('$pkgver', pkgdata.pkgver)

		if s.find('$pkgrel') >= 0:
			s = s.replace('$pkgrel', pkgdata.pkgrel)

		if s.find('$arch') >= 0:
			s = s.replace('$arch', pkgdata.arch)

		if s.find('${pkgdir}') >= 0:
			s = s.replace('${pkgdir}', pkgdir)

		if s.find('${pkgdir}') >= 0:
			s = s.replace('${pkgdir}', pkgdir)

		if s.find('${srcdir}') >= 0:
			s = s.replace('${srcdir}', srcdir)

		if s.find('$srcdir') >= 0:
			s = s.replace('$srcdir', srcdir)

		return s

	for i in pkgdata.source:
		pkgdata.source[pkgdata.source.index(i)] = replace_vars(i, pkgdata)

	for i in pkgdata.prepare_instructions:
		pkgdata.prepare_instructions[pkgdata.prepare_instructions.index(i)] = replace_vars(i, pkgdata)

	for i in pkgdata.package_instructions:
		pkgdata.package_instructions[pkgdata.package_instructions.index(i)] = replace_vars(i, pkgdata)

	pkgdata.url = replace_vars(pkgdata.url, pkgdata)



# Check
# Package

if __name__ == '__main__':
	# Check if not root
	if getuid() == 0:
		print('{} cannot be run as root.'.format('makedebpkg.py'), file=stderr)
		exit(1)

	# Parsing args
	parser = ArgumentParser()
	parser.add_argument("PKGBUILD", type=str)
	parser.add_argument('--maintainer', type=str)
	parser.add_argument('-e', '--essential', action='store_true')
	parser.add_argument('-i', '--install', action='store_true')

	args = parser.parse_args()

	# Parsing basic paths
	pkgbuild_path = args.PKGBUILD
	
	if args.maintainer:
		maintainer = args.maintainer
	elif environ.get('MAINTAINER'):
		maintainer = environ.get('MAINTAINER')
	else:
		maintainer = 'None'

	if args.essential:
		essential = True
	else:
		essential = False
	# rootpath = dirname(realpath(pkgbuild_path))
	rootpath = getcwd()
	srcdir_path = rootpath + '/src'

	if not isdir(srcdir_path):
		mkdir(srcdir_path, 700)

	# Parsing PKGBUILD
	pkgparser = PkgData()
	pkgparser.parse(pkgbuild_path)

	# Final pkgdir name
	pkgdir_name = pkgparser.pkgname + ('-' + pkgparser.pkgver if pkgparser.pkgver != '' else '')
	if pkgparser.pkgrel != '':
		pkgdir_name += '-' + pkgparser.pkgrel

	if pkgparser.epoch != 0:
		pkgdir_name += '-' + str(pkgparser.epoch)

	pkgdir = rootpath + '/' + pkgdir_name

	if not isdir(pkgdir):
		mkdir(pkgdir, 751)

	debdir = pkgdir + '/DEBIAN'
	if not isdir(debdir):
		mkdir(debdir, 751)

	# Expanding Bash vars
	expand_vars(pkgparser, srcdir_path, pkgdir)
	pkgparser.print_debug()

	# Downloading source
	dw = PkgDownloadManager(srcdir_path)

	for i in pkgparser.source:
		p = i.find('+')
		if p >= 0: 
			if i[:p] == 'git':
				dw.git(i[:p + 1])

			elif i[:p] in ['svn', 'bzr', 'hg']:
				print('{0} is currently not supported.'.format(i[:p]), file=stderr)
				exit(2)

			else:
				print('{} is an invalid VCS.'.format(i[:p]))
				exit(2)

		else:
			filename = dw.get(i)
			archive_path = srcdir_path + '/' + filename
			# Checksum dump here

			if i not in pkgparser.noextract:
				# Extract archive
				ext = filename.split('.')[-1]

				if ext == 'zip':
					with ZipFile(archive_path) as zip_file:
						zip_file.extractall(srcdir_path)

				elif ext == 'rar':
					print('.rar is currently unsupported.', file=stderr)
					exit(3)

				elif filename.split('.')[-2] == 'tar' or ext == 'tar':
					with tar_open(archive_path) as tar_file:
						tar_file.extractall(srcdir_path)


	# Building package
	if pkgparser.prepare_instructions:
		print('[ prepare() ]')
		# for i in pkgparser.prepare_instructions:
		# 	run_cmd(i).check_returncode()

	if pkgparser.build_instructions:
		print('[ build() ]')
		# for i in pkgparser.build_instructions:
		# 	run_cmd(i).check_returncode()

	if pkgparser.check_instructions:
		print('[ check() ]')
		# for i in pkgparser.check_instructions:
		# 	run_cmd(i).check_returncode()

	if pkgparser.package_instructions:
		print('[ package() ]')
		# for i in pkgparser.package_instructions:
		# 	run_cmd(i).check_returncode()


	# Generating control file
	con = ControlData()
	con.import_from_pkgdata(pkgparser, maintainer, essential)
	con.export(debdir + '/control')


	# Building deb package
	run_cmd('dpkg -b {}'.format(pkgdir))

	if args.install:
		run_cmd('dpkg -i {}'.format(pkgdir + '.deb'))