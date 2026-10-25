"""Interactive authorization, keyframe and host exit regression (mock DSH DOM)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
PLUGIN = (ROOT / 'lib/client.js').read_text(encoding='utf8')
FIXTURE = (ROOT / 'test/fixture-dsh-mock.html').read_text(encoding='utf8')
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1600, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(FIXTURE)
    page.evaluate('''() => { window.__ModuleLoader__={load(value){window.pluginBundle=value;}}; }''')
    page.add_script_tag(content=PLUGIN)
    page.evaluate('''() => { const p = window.pluginBundle.factory(()=>{throw Error('no deps')}); p.apply({effect(fn){window.cleanup=fn()}}); }''')
    frame = [f for f in page.frames if f != page.main_frame][-1]
    frame.locator('#authUnlock').wait_for(state='attached')
    frame.evaluate('''() => { window.DSHStartup.seek(6349); window.DSHStartup.play(); }''')
    frame.wait_for_function('document.getElementById("stage").dataset.phase === "auth"')
    frame.wait_for_timeout(250)
    assert '点 击 授 权 解 锁' in frame.locator('#authUnlock').inner_text()
    assert frame.locator('.auth-key.unlocked').count() == 0
    assert frame.locator('#authUnlock').is_enabled()
    assert frame.evaluate('''() => !!Array.from(document.styleSheets).flatMap(s => { try {return Array.from(s.cssRules)} catch { return [] } }).find(r => r.name === 'key-insert-ccw')''')
    assert frame.locator('.lock-interact').count()==4
    assert frame.locator('use[href="#tnolar-physical-key"]').count()==4
    rects = frame.evaluate('''() => {
      const button=document.getElementById('authUnlock').getBoundingClientRect();
      const keys=document.querySelector('.auth-keys').getBoundingClientRect();
      return { button:{top:button.top,bottom:button.bottom}, keys:{top:keys.top,bottom:keys.bottom}};
    }''')
    print('layout',rects)
    assert rects['button']['bottom']+10 < rects['keys']['top'], 'Authorization button collides with keys'
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-auth.png'))
    frame.locator('#key0 .lock-interact').click() # physical key may start authorization directly
    frame.wait_for_timeout(535)
    assert frame.locator('.auth-key.turning').count() >= 1, 'Turning animation was not triggered'
    rotation = frame.evaluate('''() => { const m = new DOMMatrix(getComputedStyle(document.querySelector('#key0 .key-rotor')).transform); return Math.atan2(m.b,m.a)*180/Math.PI }''')
    print('counterclockwise rotation at 535ms',rotation)
    assert rotation < -15, f'Key was not turning counterclockwise: {rotation}'
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-keyturn.png'))
    frame.wait_for_function('document.getElementById("stage").dataset.phase === "ready"',timeout=8000)
    assert frame.locator('.auth-key.unlocked').count() == 4
    finalRotation = frame.evaluate('''() => { const m = new DOMMatrix(getComputedStyle(document.querySelector('#key0 .key-rotor')).transform); return Math.atan2(m.b,m.a)*180/Math.PI }''')
    assert abs(finalRotation+90) < 1, f'Final key angle should be -90 degrees, got {finalRotation}'
    frame.wait_for_selector('#readyCard', state='visible', timeout=3000)
    assert frame.locator('.ready-heading').text_content() == '请您指挥'
    assert '等待命令输入' in frame.locator('.ready-desc').inner_text()
    # Completion now waits for user: host must not auto-close after 2 seconds.
    page.wait_for_timeout(2200)
    assert page.locator('#dsh-theme-tnolar-overlay').count() == 1
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-ready.png'))
    frame.locator('#enterButton').click()
    page.wait_for_timeout(450)
    assert page.locator('#dsh-theme-tnolar-overlay').count() == 0
    assert not page.locator('#root').evaluate('(r)=>r.inert')
    assert not errors, errors
    browser.close()
    print('Interactive authorization and return to host: PASS')