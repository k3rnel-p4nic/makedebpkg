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

class PkgSyntaxError(Exception):
	def __init__(self, message = 'Syntax Error: incorrect PKGBUILD'):
		super(PkgSyntaxError, self).__init__(message)

class PkgData(object):
	"""PkgData: class to manage and represent a PKGBUILD"""
	def __init__(self):
		super(PkgData, self).__init__()
		self.pkgbase = ''
		self.pkgname = ''
		self.pkgver = 0
		self.pkgrel = 0
		self.epoch = 0
		self.pkgdesc = ''
		self.arch = []
		self.url = ''
		self.license = []
		self.groups = []
		self.depends = []
		self.optdepends = []
		self.makedepends = []
		self.provides = []
		self.conflicts = []
		self.replaces = []
		self.backup = []
		self.options = []
		self.install = ''
		self.changelog = ''
		self.source = []
		self.noextract = []
		self.validpgpkeys = []
		self.checksum = ''

		self.prepare_instructions = []
		self.build_instructions = []
		self.check_instructions = []
		self.package_instructions = []


	@staticmethod
	def strip(s, substr):
		if not substr.endswith('='):
			substr += '='

		s = s[len(substr):]
		if s.endswith('\n'):
			s = s[:-1]

		if s.startswith('"') and s.endswith('"'):
			s = s[1:-1]

		return s


	@staticmethod
	def striplist(s, field):
		temp = PkgData.strip(s, field)
		if temp.startswith('(') and temp.endswith(')'):
			temp = temp[1:-1].replace("'", '')

		return temp.split(' ')


	@staticmethod
	def getNextCharIndex(start, lines, char):
		for i in range(start, len(lines)):
			if lines[i].startswith(char):
				return i

		return None

	@staticmethod
	def stripfunction(name, start, lines):
		if lines[start].startswith(name + '()' + ' {') or lines[start].startswith(name + '()' + '{'):
			# start_index = start + 1
			start += 1

		elif lines[start].startswith(name + '()'):
			start = PkgData.getNextCharIndex(start, lines, '{') + 1

		else:
			raise PkgSyntaxError

		end = PkgData.getNextCharIndex(start + 1, lines, '}')

		if not start or not end:
			raise PkgSyntaxError('Undefined behavior')

		lines = [w.replace('\t', '').replace('\n', '') for w in lines[start:end]]

		return lines


	def print_debug(self):
		print("pkgbase: " + self.pkgbase)
		print("pkgname: " + self.pkgname)
		print("pkgver: " + self.pkgver)
		print("pkgrel: " + self.pkgrel)
		print("epoch: " + str(self.epoch))
		print("pkgdesc: " + self.pkgdesc)
		print("arch: " + str(self.arch))
		print("url: " + self.url)
		print("license: " + str(self.license))
		print("groups: " + str(self.groups))
		print("depends: " + str(self.depends))
		print("optdepends: " + str(self.optdepends))
		print("makedepends: " + str(self.makedepends))
		print("provides: " + str(self.provides))
		print("conflicts: " + str(self.conflicts))
		print("replaces: " + str(self.replaces))
		print("backup: " + str(self.backup))
		print("options: " + str(self.options))
		print("install: " + self.install)
		print("changelog: " + self.changelog)
		print("source: " + str(self.source))
		print("noextract: " + str(self.noextract))
		print("validpgpkeys: " + str(self.validpgpkeys))
		print("checksum: " + self.checksum)
		print("\nprepare(): " + str(self.prepare_instructions))
		print("build(): " + str(self.build_instructions))
		print("check(): " + str(self.check_instructions))
		print("package(): " + str(self.package_instructions))


	def parse(self, filename):
		"""Fetches every relevant information from a PKGBUILD"""
		with open(filename, 'r') as file:
			# for line in file:
			lines = file.readlines()
			for i in range(0, len(lines)):
				line = lines[i]

				if line.startswith('#'):
					continue

				elif line.startswith('\n'):
					continue

				elif line.startswith('pkgbase=') and not self.pkgbase:
					self.pkgbase = self.strip(line, 'pkgbase')
				
				elif line.startswith('pkgname=') and not self.pkgname:
					self.pkgname = self.strip(line, 'pkgname')

				elif line.startswith('pkgver=') and not self.pkgver:
					self.pkgver = self.strip(line, 'pkgver')

				elif line.startswith('pkgrel=') and not self.pkgrel:
					self.pkgrel = self.strip(line, 'pkgrel')

				elif line.startswith('pkgdesc=') and not self.pkgdesc:
					self.pkgdesc = self.strip(line, 'pkgdesc')

				elif line.startswith('arch=') and not self.arch:
					self.arch = self.striplist(line, 'arch')

				elif line.startswith('url=') and not self.url:
					self.url = self.strip(line, 'url')

				elif line.startswith('license=') and not self.license:
					self.license = self.striplist(line, 'license')

				elif line.startswith('groups=') and not self.groups:
					self.groups = self.striplist(line, 'groups')

				elif line.startswith('depends=') and not self.depends:
					self.depends = self.striplist(line, 'depends')

				elif line.startswith('optdepends=') and not self.optdepends:
					tmplist = self.striplist(line, 'optdepends')

					for i in tmplist:
						if i.endswith(':'):
							temp = i

						if i == tmplist[-1] or tmplist[tmplist.index(i) + 1].endswith(':'):
							self.optdepends.append(temp[:-1])

				elif line.startswith('makedepends=') and not self.makedepends:
					self.makedepends = self.striplist(line, 'makedepends')

				elif line.startswith('provides=') and not self.provides:
					self.provides = self.striplist(line, 'provides')

				elif line.startswith('conflicts=') and not self.conflicts:
					self.conflicts = self.striplist(line, 'conflicts')

				elif line.startswith('replaces=') and not self.replaces:
					self.replaces = self.striplist(line, 'replaces')

				elif line.startswith('backup=') and not self.backup:
					self.backup = self.striplist(line, 'backup')

				elif line.startswith('options=') and not self.options:
					self.options = self.striplist(line, 'options')

				elif line.startswith('install=') and not self.install:
					self.install = self.strip(line, 'install')

				elif line.startswith('changelog=') and not self.changelog:
					self.changelog = self.strip(line, 'changelog')

				elif line.startswith('source=') and not self.source:
					self.source = self.striplist(line, 'source')
					for i in self.source:
						if i.startswith('"') and i.endswith('"'):
							self.source[self.source.index(i)] = i[1:-1]

				elif line.startswith('noextract=') and not self.noextract:
					self.noextract = self.striplist(line, 'noextract')

				elif line.startswith('validpgpkeys=') and not self.validpgpkeys:
					self.validpgpkeys = self.striplist(line, 'validpgpkeys')

				# Managing install instructions
				elif line.startswith('prepare()') and not self.prepare_instructions:
					self.prepare_instructions = self.stripfunction('prepare', i, lines)

				elif line.startswith('build()') and not self.build_instructions:
					self.build_instructions = self.stripfunction('build', i, lines)

				elif line.startswith('check()') and not self.check_instructions:
					self.check_instructions = self.stripfunction('check', i, lines)

				elif line.startswith('package()') and not self.package_instructions:
					self.package_instructions = self.stripfunction('package', i, lines)


			print("IMPLEMENT CHECKSUM")