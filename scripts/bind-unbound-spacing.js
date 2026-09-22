// bind-unbound-spacing.js
// Companion to find-unbound-spacing.js. For every unbound gap or padding inside
// the components on the current page it finds the spacing token with the same
// value, then checks what the variant's State=default twin binds for that property.
// Same token → safe to bind. Different token → a person has to decide.
// Dry run by default. Set APPLY = true to bind the safe ones.
// Run it through a Figma MCP client. Scripter's compiler is too old for it.

const APPLY = false;
const props = ['itemSpacing', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'];
const isAutoLayout = n => 'layoutMode' in n && n.layoutMode !== 'NONE';
const tokens = (await figma.variables.getLocalVariablesAsync('FLOAT')).filter(v => v.scopes.includes('GAP'));
const byValue = new Map(tokens.map(v => [Object.values(v.valuesByMode)[0], v]));
const nameOf = async ref => ref ? (await figma.variables.getVariableByIdAsync(ref.id)).name : null;
const rows = [];
for (const c of figma.currentPage.findAllWithCriteria({ types: ['COMPONENT'] })) {
  const base = c.name.replace(/State=\w+/i, '');
  const twin = c.parent?.type === 'COMPONENT_SET'
    ? c.parent.children.find(s => s !== c && /State=default/i.test(s.name) && s.name.replace(/State=\w+/i, '') === base)
    : null;
  for (const f of [c, ...c.findAll(isAutoLayout)].filter(isAutoLayout)) {
    const twinLayer = !twin ? null : f === c ? twin : twin.findOne(n => n.name === f.name);
    for (const p of props) {
      if (!(f[p] > 0) || f.boundVariables?.[p]) continue;
      const token = byValue.get(f[p]);
      const twinToken = await nameOf(twinLayer?.boundVariables?.[p]);
      const verdict = !token ? 'no token' : twinToken && twinToken !== token.name ? `default uses ${twinToken}` : 'bind';
      if (APPLY && verdict === 'bind') f.setBoundVariable(p, token);
      rows.push({ component: c.name, layer: f.name, prop: p, value: f[p], token: token?.name ?? '—', verdict });
    }
  }
}
const safe = rows.filter(r => r.verdict === 'bind').length;
console.log(`${rows.length} unbound · ${safe} safe to bind · ${rows.length - safe} need a person`);
for (const r of rows) console.log(`${r.verdict.padEnd(24)} ${r.value}px → ${r.token}   ${r.component} › ${r.layer} (${r.prop})`);
