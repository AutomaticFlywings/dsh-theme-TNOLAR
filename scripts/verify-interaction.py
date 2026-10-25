"""DSH startup auth mechanics: insertion, axial twist, shared lock pose, host exit."""
from pathlib import Path
import math
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

    # Deterministic scene for snapshot capture; the real click path is checked after this.
    def seek(time_ms):
        frame.evaluate('ms => window.DSHStartup.seek(ms)', time_ms)
        frame.wait_for_timeout(100)
    def pose(key_index=0):
        return frame.evaluate('''id => {
          const lock=document.querySelector(`#key${id} .lock-interact`);
          const key=document.querySelector(`#key${id} .key-rotor`);
          const core=document.querySelector(`#key${id} .lock-core`);
          const matrixYaw=transform=>{
            const m=new DOMMatrixReadOnly(transform);
            return Math.atan2(-m.m13,m.m11)*180/Math.PI;
          };
          const style=getComputedStyle(lock);
          const bounding=key.getBoundingClientRect();
          return {
            yaw:parseFloat(style.getPropertyValue('--tnolar-key-yaw')),
            depth:parseFloat(style.getPropertyValue('--tnolar-key-depth')),
            bladeYaw:matrixYaw(getComputedStyle(key).transform),
            slotYaw:matrixYaw(getComputedStyle(core,'::before').transform),
            keyTop:bounding.y, projectedWidth:bounding.width,
          };
        }''', key_index)
    def sync(a):
        assert abs(a['bladeYaw']-a['slotYaw']) < 0.6, f'Key and slot diverged: {a}'
        assert abs(a['yaw']-a['slotYaw']) < 0.6, f'CSS shared pose diverged: {a}'

    seek(6350)
    frame.wait_for_timeout(780)  # let phase-change overlay transitions finish
    standby=pose()
    sync(standby)
    assert standby['depth'] > 3.0, standby
    assert abs(standby['yaw']-76)<0.5, standby
    assert frame.locator('#authUnlock').inner_text() == '授 权 解 锁'
    assert frame.locator('.auth-hint').count() == 0
    assert frame.locator('.auth-key.unlocked').count() == 0
    assert frame.locator('#authUnlock').is_enabled()
    assert frame.locator('.lock-interact').count()==4
    assert frame.locator('use[href="#tnolar-physical-key"]').count()==4
    rects = frame.evaluate('''() => {
      const b=document.getElementById('authUnlock').getBoundingClientRect();
      const k=document.querySelector('.auth-keys').getBoundingClientRect();
      return {buttonBottom:b.bottom,keyTop:k.top};
    }''')
    assert rects['buttonBottom']+10 < rects['keyTop'], f'Button overlaps key group: {rects}'
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-auth.png'))

    # Use the actual user-facing click to check the transition into the cycle.
    frame.locator('#key0 .lock-interact').click()
    frame.wait_for_timeout(240)
    inserted=pose()
    sync(inserted)
    assert inserted['depth'] < standby['depth'] - .3, f'Insertion does not travel: {standby} -> {inserted}'
    assert abs(inserted['yaw']-standby['yaw']) < .6, f'Rotation started before insertion: {inserted}'
    assert inserted['keyTop'] < standby['keyTop'] - 5, 'Physical key did not slide upward'
    assert frame.locator('#authUnlock').is_disabled()

    # Seek gives exact, repeatable keyframes without depending on CPU frame rate.
    seek(6350+440)
    seated=pose()
    sync(seated)
    assert abs(seated['depth']) < .12, f'Key did not reach the lock: {seated}'
    assert abs(seated['yaw']-76) < .6, f'Key turned during insertion: {seated}'

    seek(6350+900)
    twisting=pose()
    sync(twisting)
    assert twisting['depth'] < .03 and 0 < twisting['yaw'] < 55, twisting
    assert twisting['projectedWidth'] > standby['projectedWidth'] * 1.7, 'Key edge-to-face twist is not visible'
    assert frame.locator('.auth-key.turning').count() >= 1
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-keyturn.png'))

    seek(7710)
    final=pose()
    sync(final)
    assert abs(final['yaw']+14)<.7, final
    assert frame.locator('#key0').evaluate('(e)=>e.classList.contains("unlocked")')
    assert frame.locator('#key1').evaluate('(e)=>!e.classList.contains("unlocked")')

    # Sequence must end normally, retain the user-confirmed ENTER step, and
    # never auto-close the host overlay at the animation completion event.
    seek(6350)
    frame.locator('#authUnlock').click()
    frame.wait_for_function('document.getElementById("stage").dataset.phase === "ready"', timeout=9000)
    assert frame.locator('.auth-key.unlocked').count() == 4
    frame.wait_for_selector('#readyCard', state='visible', timeout=3000)
    assert frame.locator('.ready-heading').text_content() == '请您指挥'
    assert '等待命令输入' in frame.locator('.ready-desc').inner_text()
    assert 'INSERT' not in frame.locator('body').inner_text()
    assert 'AXIAL TWIST' not in frame.locator('body').inner_text()
    page.wait_for_timeout(2200)
    assert page.locator('#dsh-theme-tnolar-overlay').count()==1
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-ready.png'))
    frame.locator('#enterButton').click()
    page.wait_for_timeout(450)
    assert page.locator('#dsh-theme-tnolar-overlay').count()==0
    assert not page.locator('#root').evaluate('(r)=>r.inert')
    assert not errors, errors
    print('Key insertion and lock-slot axial synchronization, four-key authorization and host exit: PASS')
    browser.close()