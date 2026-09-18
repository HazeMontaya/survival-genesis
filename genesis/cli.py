import argparse,json
from genesis.runtime.agent import GenesisAgent
from genesis.runtime.server import serve
def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest="command");s.add_parser("status");s.add_parser("tick");v=s.add_parser("serve");v.add_argument("--host",default="127.0.0.1");v.add_argument("--port",type=int,default=8765);a=p.parse_args();g=GenesisAgent()
 if a.command=="status":print(json.dumps(g.snapshot(),indent=2,ensure_ascii=False))
 elif a.command=="tick":print(json.dumps(g.tick(),indent=2,ensure_ascii=False))
 elif a.command=="serve":serve(a.host,a.port)
 else:p.print_help()
if __name__=="__main__":main()
