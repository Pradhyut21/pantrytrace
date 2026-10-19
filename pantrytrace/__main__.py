"""python -m pantrytrace: reproducible demo, evaluation and workbench."""
import argparse
import json
from pathlib import Path
import sys

from . import export_action_packet, list_scenarios, run_case, run_evaluation


def main():
    # Windows redirected stdout can otherwise use cp1252, while evidence and
    # trace values contain Unicode. JSON command output is always UTF-8.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="PantryTrace internal recall reconciliation prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    web = sub.add_parser("serve", help="Open the loopback-only fixture workbench")
    web.add_argument("--port", type=int, default=8765)
    demo = sub.add_parser("demo", help="Run a synthetic case with an auditable trace")
    demo.add_argument("--scenario", default="ambiguous", choices=[s["id"] for s in list_scenarios()])
    demo.add_argument("--output", type=Path)
    demo.add_argument("--packet", type=Path)
    demo.add_argument("--memory", action="store_true", help="Use the real local Meterless H-MEM engine; requires npm ci")
    evaluation = sub.add_parser("evaluate", help="Evaluate the labeled synthetic cases")
    evaluation.add_argument("--output", type=Path)
    sub.add_parser("doctor", help="Show sponsor configuration without exposing secrets")
    smoke = sub.add_parser("sponsor-smoke", help="Execute a real isolated local Meterless persistence check")
    smoke.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "serve":
        from .server import serve
        return serve(args.port)
    if args.command == "sponsor-smoke":
        from .sponsors import meterless_smoke
        result = meterless_smoke()
    elif args.command == "doctor":
        try:
            from .sponsors import integration_status
            result = integration_status()
        except ImportError:
            result = {"mode": "fixture", "sponsor_connections": "not configured"}
    elif args.command == "evaluate":
        result = run_evaluation()
    else:
        memory_client, prior = None, None
        if args.memory:
            from .memory import consult_memory
            memory_client, prior = consult_memory(args.scenario)
        result = run_case(args.scenario)
        if memory_client:
            from .memory import retain_investigation
            result = retain_investigation(result, memory_client, prior)
        if args.packet:
            args.packet.parent.mkdir(parents=True, exist_ok=True)
            args.packet.write_text(json.dumps(export_action_packet(result), indent=2), encoding="utf-8")
    output = getattr(args, "output", None)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
        print(f"Saved {output}")
    else:
        print(text)


if __name__ == "__main__":
    from .sponsors import SponsorError
    try:
        main()
    except SponsorError as error:
        parser_message = "Sponsor operation stopped: " + str(error)
        print(parser_message, file=sys.stderr)
        raise SystemExit(1)
