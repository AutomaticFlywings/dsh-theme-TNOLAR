"""Optional Playwright-based integration smoke (system Chromium required).

Checks the standalone bundle in a DOM fixture with CSS module class names
matching the upstream DSH source. Not a full real-DSH integration test.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = (ROOT / 'lib/client.js').read_text(encoding='utf-8')
FIXTURE = (ROOT / 'test/fixture-dsh-mock.html').read_text(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1600, 'height': 900}, device_scale_factor=1)
    errors=[]
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(FIXTURE)
    result=page.evaluate('''async (source) => {
      const url = URL.createObjectURL(new Blob([source], {type:'text/javascript'}));
      try {
        const plugin = await import(url);
        plugin.apply({effect(fn){window.tnolarCleanup=fn();}});
        return {name:plugin.name,theme:!!document.getElementById('dsh-theme-tnolar-theme-style')};
      } finally {URL.revokeObjectURL(url)}
    }''', PLUGIN)
    assert result == {'name':'dsh-theme-tnolar','theme':True}, result
    assert page.locator('html[data-tnolar-theme="1"]').count()==1
    assert page.locator('#dsh-theme-tnolar-overlay iframe').count()==1
    frame = [f for f in page.frames if f != page.main_frame][-1]
    frame.wait_for_load_state('load')
    nodes=frame.evaluate("document.querySelectorAll('.map-node').length")
    links=frame.evaluate("document.querySelectorAll('.route-active').length")
    assert (nodes,links)==(9,14),(nodes,links)
    frame.evaluate("window.DSHStartup.seek(14400);document.querySelector('.geo-svg').style.transition='none';document.getElementById('readyCard').classList.add('hidden')")
    page.wait_for_timeout(1200)
    page.screenshot(path=str(ROOT/'docs/preview-tnolar-map.png'),full_page=True)
    page.evaluate("window.DSHTNOLAR.skip()")
    page.wait_for_timeout(440)
    assert page.locator('#dsh-theme-tnolar-overlay').count()==0
    assert not page.locator('#root').evaluate('(element)=>element.inert')
    values=page.evaluate('''() => {
      const style = (selector) => getComputedStyle(document.querySelector(selector));
      const root=style('#root');
      const session=style('.sessionRow__qa.selected__qa');
      const card=style('.InputBar_card__qa');
      const header=style('.ConversationRoot_header__qa');
      const button=style('.InputBar_primary__qa');
      return {
        bg:root.getPropertyValue('--dsw-alias-bg-base').trim(),
        navBg:style('.sidebarCol__qa').backgroundImage,
        selectedColor:session.backgroundImage,
        selectedInset:session.boxShadow,
        cardBorder:card.borderTopColor,
        cardRadius:card.borderTopLeftRadius,
        headerBg:header.backgroundImage,
        buttonRadius:button.borderTopLeftRadius,
        sourceCss:!!document.getElementById('dsh-theme-tnolar-theme-style'),
      };
    }''')
    print('Theme values:',values)
    assert values['bg']=='#06131b'
    assert values['selectedColor'].startswith('linear-gradient')
    assert 'inset' in values['selectedInset']
    assert values['cardRadius']=='13px'
    assert values['buttonRadius']=='6px'
    assert values['headerBg'].startswith('linear-gradient')
    page.screenshot(path=str(ROOT/'docs/preview-tnolar-theme.png'),full_page=True)
    # Confirm immediate disable / re-enable, and destruction roll back the theme.
    page.evaluate('window.DSHTNOLAR.setThemeEnabled(false)')
    assert page.locator('html[data-tnolar-theme="1"]').count()==0
    assert page.locator('#dsh-theme-tnolar-theme-style').count()==0
    page.evaluate('window.DSHTNOLAR.setThemeEnabled(true)')
    assert page.locator('html[data-tnolar-theme="1"]').count()==1
    page.evaluate('window.DSHTNOLAR.replay()')
    assert page.locator('#dsh-theme-tnolar-overlay iframe').count()==1
    page.evaluate('window.tnolarCleanup()')
    assert page.locator('#dsh-theme-tnolar-overlay').count()==0
    assert page.locator('#dsh-theme-tnolar-theme-style').count()==0
    assert page.locator('html[data-tnolar-theme="1"]').count()==0
    assert not page.locator('#root').evaluate('(element)=>element.inert')
    print('Browser integration checks: PASS; errors:',errors)
    assert not errors
    browser.close()