from fit import FitFile

import sys

def main():
    fit_file = sys.argv[1]
    with FitFile.open(fit_file) as f:
        for message in f:
            print(message)


if __name__ == "__main__":
    main()
