"""Fetch explicitly scoped Zetaris views; run the same engine with no fixture reads.

This command performs real reads only when the user supplies valid sponsor access.
It fails closed on truncation, schema ambiguity, provider failure, or missing memory.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pantrytrace import run_connected_records
from pantrytrace.memory import consult_memory, retain_investigation
from pantrytrace.sponsors import NvidiaClient, SponsorError, ZetarisClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('recall','inventory','intake','aliases','transfers'):
        parser.add_argument('--'+name+'-view', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--nvidia-critique', action='store_true')
    args = parser.parse_args()
    zetaris = ZetarisClient.from_env()
    sources = {}
    receipts = []
    for name in ('recall','inventory','intake','aliases','transfers'):
        view = getattr(args, name+'_view')
        rows = zetaris.fetch_table(view, limit=5000)
        if len(rows) >= 5000:
            raise SponsorError('View may be truncated; supply a smaller investigation-scoped view.')
        sources[name] = rows
        receipts.append({'view':view,'rows':len(rows),'retrieved_at':datetime.now(timezone.utc).isoformat()})
    if len(sources['recall']) != 1:
        raise SponsorError('The recall view must return exactly one bounded notice.')
    recall = sources['recall'][0]
    for field in ('affected_gtins','affected_lots'):
        if isinstance(recall.get(field), str):
            try:
                recall[field] = json.loads(recall[field])
            except ValueError:
                raise SponsorError(f'{field} must be a JSON array, not free text.') from None
    for name in ('inventory','intake','transfers'):
        for row in sources[name]:
            if isinstance(row.get('units'), str):
                try:
                    row['units'] = int(row['units'])
                except ValueError:
                    raise SponsorError('Units must be explicit whole-number quantities.') from None
    client, prior = consult_memory('connected')
    result = run_connected_records(recall=recall, inventory=sources['inventory'],
        intake_rows=sources['intake'], supplier_aliases=sources['aliases'], transfers=sources['transfers'],
        provenance={'provider':'Zetaris','actual_reads_completed':True,'query_receipts':receipts,
                    'sources': {'recall': args.recall_view, 'inventory': args.inventory_view,
                                'ledger': args.intake_view, 'aliases': args.aliases_view,
                                'transfers': args.transfers_view}})
    result = retain_investigation(result, client, prior)
    result['zetaris'] = {'verified':True,'scope':'actual read-only view queries; no production validation','receipts':receipts}
    if args.nvidia_critique:
        result['nvidia_critique'] = {'text': NvidiaClient.from_env().critique(json.dumps(result['decisions'])),
                                    'scope':'advisory text only; does not override evidence policy'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Saved connected investigation with actual provider receipts:',args.output)


if __name__ == '__main__':
    try:
        main()
    except (SponsorError,ValueError,TypeError) as error:
        print('Connected investigation stopped:', error, file=sys.stderr)
        raise SystemExit(1)
