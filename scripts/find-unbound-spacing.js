// find-unbound-spacing.js
// Lists every auto-layout frame inside the components on the current page
// whose gap or padding is a hardcoded value instead of a bound variable.
// Run it through a Figma MCP client. Scripter's compiler is too old for it.

const props = ['itemSpacing', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'];
const isAutoLayout = n => 'layoutMode' in n && n.layoutMode !== 'NONE';
const components = figma.currentPage.findAllWithCriteria({ types: ['COMPONENT'] });
const misses = []; let checked = 0;
for (const c of components) {
  for (const f of [c, ...c.findAll(isAutoLayout)].filter(isAutoLayout)) {
    checked++;
    const bound = f.boundVariables || {};
    const open = props.filter(p => f[p] > 0 && !bound[p]);
    if (open.length) misses.push({ component: c.name, layer: f.name, unbound: open.join(', ') });
  }
}
console.log(`${checked} auto-layout frames checked · ${misses.length} with unbound spacing`);
console.table(misses);
