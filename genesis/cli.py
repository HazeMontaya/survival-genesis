import argparse
import json
from .agent import GenesisAgent

def main() -> None:
    parser = argparse.ArgumentParser(prog="survival-genesis")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")
    sub.add_parser("tick")

    args = parser.parse_args()
    agent = GenesisAgent()

    if args.command == "status":
        print(json.dumps(agent.snapshot(), indent=2))
    elif args.command == "tick":
        print(json.dumps(agent.tick(), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
