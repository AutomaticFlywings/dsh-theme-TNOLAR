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
    assert frame.locator('#authUnlock').inner_text() == '授 权 解 锁'
    assert frame.locator('.auth-hint').count() == 0
    assert frame.locator('#authLine').inner_text() == 'AUTHORIZATION PENDING'
    assert frame.locator('.auth-key.unlocked').count() == 0
    assert frame.locator('#authUnlock').is_enabled()
    assert frame.evaluate('''() => !!Array.from(document.styleSheets).flatMap(s => { try {return Array.from(s.cssRules)} catch { return [] } }).find(r => r.name === 'key-insert-cw')''')
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
    startTransform = frame.evaluate("() => getComputedStyle(document.querySelector('#key0 .key-rotor')).transform")
    frame.locator('#key0 .lock-interact').click() # physical key may start authorization directly
    frame.wait_for_timeout(535)
    assert frame.locator('.auth-key.turning').count() >= 1, 'Turning animation was not triggered'
    midTransform = frame.evaluate("() => getComputedStyle(document.querySelector('#key0 .key-rotor')).transform")
    # The key shaft AND the lock-slot must rotate about the same longitudinal
    # Y axis, with identical phase/angle; a Z-spin of the slot is a regression.
    yaw = frame.evaluate('''() => {
      const matrixYaw = value => {
        const m = new DOMMatrixReadOnly(value);
        return Math.atan2(-m.m13,m.m11)*180/Math.PI;
      };
      return {
        key:matrixYaw(getComputedStyle(document.querySelector('#key0 .key-rotor')).transform),
        slot:matrixYaw(getComputedStyle(document.querySelector('#key0 .lock-core'),'::before').transform),
      };
    }''')
    print('key/lock slot axial yaw at 535ms', yaw)
    assert abs(yaw['key']-yaw['slot']) < 3, f'Key and lock slot were not synchronized: {yaw}'
    assert midTransform != startTransform, f'Key was not axially twisting: start={startTransform}, now={midTransform}'
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-keyturn.png'))
    frame.wait_for_function('document.getElementById("stage").dataset.phase === "ready"',timeout=8000)
    assert frame.locator('.auth-key.unlocked').count() == 4
    assert '密钥沿轴' not in frame.locator('body').inner_text()
    finalTransform = frame.evaluate("() => getComputedStyle(document.querySelector('#key0 .key-rotor')).transform")
    assert finalTransform != startTransform, f'Final key transform should differ from initial, got {finalTransform}'
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