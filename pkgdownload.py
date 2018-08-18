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


from urllib.request import urlopen
from git import Repo as g
from os.path import exists as path_exists


class PkgDownloadManager(object):
	"""Simple Download Manager class"""
	def __init__(self, rootdir):
		super(PkgDownloadManager, self).__init__()
		self.__rootdir = rootdir


	def get(self, url):
		"""Simple HTTP/GET request with progress bar to retrieve a file"""
		# Progress bar thanks to https://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
		u = urlopen(url)
		meta = u.info()
		filename = meta['Content-Disposition'][meta['Content-Disposition'].find('filename=') + 9:]    # Translating index of 'filename='.size()

		if path_exists(self.__rootdir + '/' + filename):
			return filename

		with open(self.__rootdir + '/' + filename, 'wb') as f:
			filesize = int(meta['Content-Length'])

			print('[ Download ] {0}: {1} Bytes'.format(filename, filesize))

			filesize_dl = 0
			blocksz = 8192

			buffer = u.read(blocksz)
			while buffer:
				filesize_dl += len(buffer)
				f.write(buffer)
				status = r"%10d  [%3.2f%%]" % (filesize_dl, filesize_dl * 100. / filesize)

				print(status)
				buffer = u.read(blocksz)

			return filename
			

	def git(self, url):
		"""Simple git clone method"""
		path = self.__rootdir + url.split('/')[-1]
		g.clone_from(url, path)