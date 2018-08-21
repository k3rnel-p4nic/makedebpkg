PROG_NAME = makedebpkg
INSTALL_PATH = /usr/lib/libmakedebpkg/
BIN_PATH = /usr/bin/makedebpkg


gen_bin:
	@printf "#!/bin/bash\n/usr/bin/env python3 %s%s.py \$$@" "${INSTALL_PATH}" "${PROG_NAME}" > ${PROG_NAME}

install:
	install -b -d -m751 *.py ${INSTALL_PATH}
	gen_bin
	install -b -d -m711 ${PROG_NAME} ${BIN_PATH}