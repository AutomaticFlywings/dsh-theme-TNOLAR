import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(resolve(root, 'assets/world-startup.html'), 'utf8');
function parseArray(ident) {
  const m = html.match(new RegExp(`const ${ident}=\\[([\\s\\S]*?)\\n \\];`));
  assert.ok(m, `${ident} missing`);
  return m[1];
}
const data = parseArray('NETWORK_NODES');
const nodes = [...data.matchAll(/\{code:'(C-\d{2})',name:'([^']+)'/g)];
const pairs = [...parseArray('ROUTE_CODES').matchAll(/\['(C-\d{2})','(C-\d{2})'\]/g)].map(([,a,b])=>[a,b]);
const expected = [
  ['C-07','C-06'],['C-06','C-04'],['C-04','C-03'],['C-03','C-02'],['C-02','C-01'],
  ['C-06','C-05'],['C-05','C-01'],['C-07','C-09'],['C-09','C-08'],['C-08','C-01'],
  ['C-06','C-08'],['C-06','C-09'],['C-05','C-04'],['C-05','C-09']
];

test('exactly 9 real-capital nodes and Paris removed',()=>{
  assert.equal(nodes.length,9);
  assert.deepEqual(nodes.map(m=>m[1]),Array.from({length:9},(_,i)=>`C-${String(i+1).padStart(2,'0')}`));
  assert.ok(!nodes.some(m=>m[2].toUpperCase()==='PARIS'));
  assert.deepEqual(nodes.map(m=>m[2]), ['WASHINGTON, D.C.','LONDON','BERLIN','MOSCOW','NEW DELHI','BEIJING','TOKYO','BRASILIA','CANBERRA']);
});
test('exactly 14 directed segments and no duplicate pairs',()=>{
  assert.deepEqual(pairs,expected);
  assert.equal(pairs.length,14);
  const keys = pairs.map(p=>p.join('->'));
  assert.equal(new Set(keys).size,14);
  const ids = new Set(nodes.map(m=>m[1]));
  pairs.forEach(([a,b])=>{assert.ok(ids.has(a));assert.ok(ids.has(b));assert.notEqual(a,b)});
});
test('all world network labels are consistent',()=>{
  assert.match(html,/CAPITAL MESH 09 NODES · 14 LINKS/);
  assert.doesNotMatch(html,/LINKS \[45\]/);
  assert.doesNotMatch(html,/10 个首都节点/);
});