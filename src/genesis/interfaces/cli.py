import argparse
import json
from genesis.runtime.agent import GenesisAgent
from genesis.interfaces.server import serve

def main() -> None:
    parser = argparse.ArgumentParser(prog="survival-genesis")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("status"); sub.add_parser("tick")
    live = sub.add_parser("serve"); live.add_argument("--host", default="127.0.0.1"); live.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(); agent = GenesisAgent()
    if args.command == "status": print(json.dumps(agent.snapshot(), indent=2))
    elif args.command == "tick": print(json.dumps(agent.tick(), indent=2))
    elif args.command == "serve": serve(args.host, args.port)
    else: parser.print_help()

if __name__ == "__main__": main()
