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
