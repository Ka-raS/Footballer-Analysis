import sys

from . import program


def main() -> None:
    from_archives = '--archives' in sys.argv
    program.run(from_archives)

if __name__ == '__main__':
    main()