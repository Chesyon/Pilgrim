 #  Copyright 2025 Chesyon
 #
 #  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
 #  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
 #  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

import logging
from pilgrim import main as pilgrim_main


def main():
    pilgrim_main()


def cli():
    try:
        main()
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()
