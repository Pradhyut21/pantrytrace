'use strict';
const el = id => document.getElementById(id);
let latest = null;
const statusLabels = {quarantine: 'PROPOSE QUARANTINE', review: 'HUMAN REVIEW', clear: 'OUTSIDE THIS RECALL'};
function node(tag, text, className) { const n = document.createElement(tag); if(text !== undefined) n.textContent = String(text); if(className) n.className = className; return n; }
function evidenceValue(value) { return typeof value === 'object' ? JSON.stringify(value) : String(value ?? ''); }
function showEvidence(decision) {
  el('evidence-title').textContent = decision.product + ' / ' + (decision.lot || 'lot unresolved');
  el('evidence-reason').textContent = decision.reason;
  el('evidence-list').replaceChildren();
  for (const evidence of decision.evidence || []) {
    const row = node('div', undefined, 'evidence-line');
    row.append(node('span', evidence.source + ' / ' + (evidence.id || '')), node('span', (evidence.field ? evidence.field + ': ' : '') + evidenceValue(evidence.value)));
    el('evidence-list').append(row);
  }
  for(const row of el('decision-rows').children) row.classList.toggle('selected-row', row.dataset.id === String(decision.id));
}
function render(result) {
  latest = result;
  el('empty').hidden = true; el('results').hidden = false;
  const summary = result.summary;
  el('affected').textContent = summary.affected_units ?? 0;
  el('review').textContent = summary.review_units ?? 0;
  el('cleared').textContent = summary.cleared_units ?? 0;
  el('iterations').replaceChildren(document.createTextNode(String(summary.iterations ?? 1)), node('span', ' passes'));
  el('loop-note').textContent = (summary.iterations > 1) ? 'Evaluator requested additional evidence' : 'Evidence checked before decisions';
  el('decision-count').textContent = result.decisions.length + ' STOCK RECORDS';
  el('run-meta').textContent = (result.duration_ms ?? 0).toFixed(0) + ' ms / fixture';
  el('decision-rows').replaceChildren();
  for(const decision of result.decisions) {
    const row = node('tr'); row.dataset.id = decision.id;
    const product = node('td'); product.append(node('strong', decision.product), node('small', decision.location + ' / ' + decision.item_id));
    const lot = node('td', decision.lot || 'Unresolved');
    const units = node('td', decision.units);
    const status = node('td'); status.append(node('span', statusLabels[decision.status] || decision.status, 'status ' + decision.status));
    const action = node('td'); const button = node('button', '↗', 'row-select'); button.setAttribute('aria-label', 'Inspect evidence for ' + decision.product); button.addEventListener('click', () => showEvidence(decision)); action.append(button);
    row.append(product, lot, units, status, action); el('decision-rows').append(row);
  }
  el('trace-list').replaceChildren();
  for(const [index, event] of (result.trace || []).entries()) {
    const critic = /reject|missing|critique|retry|conflict/i.test([event.action,event.status].join(' '));
    const item = node('li', undefined, 'trace-step' + (critic ? ' critique' : ''));
    const detail = node('div'); detail.append(node('h4', event.agent + ' / ' + event.action), node('p', event.detail), node('small', 'PASS ' + event.iteration + ' · ' + event.status));
    item.append(node('span', String(index + 1).padStart(2, '0'), 'trace-count'), detail); el('trace-list').append(item);
  }
  el('task-copy').textContent = (result.tasks || []).length + ' draft tasks carry their evidence. A person approves every operational action.';
  if(result.decisions.length) showEvidence(result.decisions.find(d => d.status === 'quarantine') || result.decisions[0]);
}
async function investigate() {
  const button = el('run'); button.disabled = true; button.querySelector('span').textContent = 'Investigating…'; el('error').hidden = true;
  try {
    const response = await fetch('/api/run', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({scenario:el('scenario').value, mode:'fixture'})});
    const result = await response.json(); if(!response.ok) throw new Error(result.error || 'Investigation failed');
    render(result);
  } catch(error) { el('error').textContent = error.message + '. Start the app with python -m pantrytrace serve.'; el('error').hidden = false; }
  finally { button.disabled = false; button.querySelector('span').textContent = 'Run investigation again'; }
}
el('run').addEventListener('click', investigate);
el('download').addEventListener('click', () => {
  if(!latest) return;
  const packet = {schema_version:'1.0', kind:'internal_recall_triage_draft', human_approval_required:true, disclosure:'Synthetic pre-event prototype. No operational action performed.', ...latest};
  const url = URL.createObjectURL(new Blob([JSON.stringify(packet,null,2)],{type:'application/json'}));
  const link = node('a'); link.href=url; link.download='pantrytrace-'+latest.scenario+'-evidence.json'; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
});
