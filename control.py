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


from pkgdata import PkgData


class ControlData(object):
	"""Container for control file fields"""
	def __init__(self):
		super(ControlData, self).__init__()
		self.package = ''
		self.version = ''
		self.description = ''
		self.architecture = []
		self.maintainer = ''
		self.essential = False
		self.homepage = ''
		self.depends = []
		self.recommends = []
		self.conflicts = []
		self.replaces = []
		self.provides = []
		self.bugs = '' # Currently not used
		# self.section = ''
		# self.priority = ''
		# self.origin = ''
		# self.tag = []
		# self.source = ''
		# self.pre_depends = []
		# self.suggests = []
		# self.breaks = []


	def import_from_pkgdata(self, pkgdata: PkgData, maintainer, essential = False):
		if not isinstance(pkgdata, PkgData):
			raise TypeError("Invalid type for pkgdata.")

		self.package = pkgdata.pkgname
		self.version = pkgdata.pkgver + ('-' + pkgdata.pkgrel if pkgdata.pkgrel else '') + ('-' + pkgdata.epoch if pkgdata.epoch else '')
		self.description = pkgdata.pkgdesc

		for i in pkgdata.arch:
			if i == 'any':
				i = 'all'
			self.architecture.append(i)

		self.homepage = pkgdata.url
		self.depends = pkgdata.depends
		self.recommends = pkgdata.optdepends
		self.provides = pkgdata.provides
		self.conflicts = pkgdata.conflicts
		self.replaces = pkgdata.replaces
		self.maintainer = maintainer
		self.essential = essential

		return self


	def export(self, filepath):
		with open(filepath, 'w') as f:
			f.write('Package: {}\n'.format(self.package))
			f.write('Version: {}\n'.format(self.version))
			if self.description:
				f.write('Description: {}\n'.format(self.description))
			
			f.write('Architecture: {}\n'.format(' '.join(self.architecture)))
			if self.homepage:
				f.write('Homepage: {}\n'.format(self.homepage))
			if self.depends:
				f.write('Depends: {}\n'.format(', '.join(self.depends)))
			if self.recommends:
				f.write('Recommends: {}\n'.format(', '.join(self.recommends)))
			if self.provides:
				f.write('Provides: {}\n'.format(', '.join(self.provides)))
			if self.conflicts:
				f.write('Conflicts: {}\n'.format(', '.join(self.conflicts)))
			if self.replaces:
				f.write('Replaces: {}\n'.format(', '.join(self.replaces)))

			f.write('Maintainer: {}\n'.format(self.maintainer))
			f.write('Essential: {}'.format('yes' if self.essential else 'no'))
			f.write('\n')
