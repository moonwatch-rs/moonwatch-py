from moonwatch.cli.main import MoonwatchCLI
import sys


if __name__ == "__main__":
    sys.exit(MoonwatchCLI().run(sys.argv[1:]))
