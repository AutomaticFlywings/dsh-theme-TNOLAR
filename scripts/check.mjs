import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
const root=resolve(import.meta.dirname,'..');
const json=JSON.parse(readFileSync(resolve(root,'package.json'),'utf8'));
const html=readFileSync(resolve(root,'assets/world-startup.html'),'utf8');
const client=readFileSync(resolve(root,'lib/client.js'),'utf8');
const template=readFileSync(resolve(root,'src/client.template.js'),'utf8');
const themeCss=readFileSync(resolve(root,'src/tnolar-theme.css'),'utf8');
const patch=readFileSync(resolve(root,'cordis.patch.yml'),'utf8');
assert.equal(json.name,'dsh-theme-tnolar');
assert.match(patch,/id: dsh-theme-tnolar/);
assert.match(patch,/name: dsh-theme-tnolar/);
assert.match(client,/export const name = 'dsh-theme-tnolar'/);
assert.equal(client,template.replace('__STARTUP_HTML_JSON__',JSON.stringify(html)).replace('__TNOLAR_THEME_CSS_JSON__',JSON.stringify(themeCss)),'Prebuilt client must exactly match source assets and theme');
assert.equal(json.dsh?.bundle?.patch, './cordis.patch.yml');
assert.equal(json.dsh?.client?.platform, 'web');
assert.equal(json.exports['./client'], './lib/client.js');
assert.equal(json.scripts.prepare, undefined, 'Git installation should not require prepare/build permissions');
assert.match(html, /const NETWORK_NODES=\[/);
assert.match(html, /WASHINGTON, D\.C\./);
assert.match(html, /CANBERRA/);
assert.match(html, /CAPITAL HUBS/);
assert.match(client, /installThemeStyles\(/);
for(const selector of ['sessionRow','panelRow','titleRow','InputBar_card','InputBar_primary','newSession','sidebarCol']){
 assert.ok(themeCss.includes(selector),`Missing styled DSH component: ${selector}`);
}
assert.match(themeCss, /--dsw-alias-bg-base/);
assert.match(themeCss, /--dsw-radius-md/);
assert.match(themeCss, /data-tnolar-theme/);
assert.match(client, /function createOverlay\(/);
assert.match(client, /frame\.setAttribute\('sandbox', 'allow-scripts'\)/);
assert.match(client, /const MAX_DURATION_MS = 19000/);
assert.match(html, /window\.addEventListener\('dsh:startup-complete'/);
for (const file of ['lib/index.js','lib/client.js','cordis.patch.yml','licenses/GSHHG-LGPL-3.txt','THIRD_PARTY_NOTICES.md']) {
  assert.ok(existsSync(resolve(root,file)), 'Missing '+file);
}
const match=html.match(/const NETWORK_NODES=\[([\s\S]*?)\n \];/);
assert.ok(match);
assert.equal((match[1].match(/\{code:'C-\d{2}'/g)||[]).length,9);
const routeMatch=html.match(/const ROUTE_CODES=\[([\s\S]*?)\n \];/);
assert.ok(routeMatch);
assert.equal((routeMatch[1].match(/\['C-\d{2}','C-\d{2}'\]/g)||[]).length,14);
assert.match(html, /CAPITAL MESH 09 NODES · 14 LINKS/);
console.log('Package manifest, assets, 9-capital/14-link rule, theme startup client setup: PASS');