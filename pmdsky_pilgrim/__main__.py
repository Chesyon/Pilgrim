import logging


def main():
    print("This will do things in the final product!")


def cli():
    try:
        main()
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()
