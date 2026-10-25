"""Four simulated fingerprint readers: progressive scan, pass feedback, host exit.

These are purely visual demonstrations. No biometric sensor or fingerprint data
is used, created, stored, or sent anywhere.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
PLUGIN=(ROOT/'lib/client.js').read_text(encoding='utf-8')
FIXTURE=(ROOT/'test/fixture-dsh-mock.html').read_text(encoding='utf-8')

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.set_content(FIXTURE)
    page.evaluate('''() => {window.__ModuleLoader__={load(value){window.pluginBundle=value}}}''')
    page.add_script_tag(content=PLUGIN)
    page.evaluate('''() => {const plugin=window.pluginBundle.factory(()=>{throw Error('no dependencies')});plugin.apply({effect(fn){window.cleanup=fn()}})}''')
    frame=[f for f in page.frames if f != page.main_frame][-1]
    frame.locator('#authUnlock').wait_for(state='attached')

    def seek(ms):
        frame.evaluate('ms => window.DSHStartup.seek(ms)',ms)
        frame.wait_for_timeout(110)

    def state(index=0):
        return frame.evaluate('''i => {
            const unit=document.querySelector(`#fp${i}`),button=unit.querySelector('.fp-touch');
            const css=getComputedStyle(button);const beam=getComputedStyle(unit.querySelector('.fp-scanline'));
            return {pct:parseFloat(css.getPropertyValue('--scan-pct')),
                beamY:parseFloat(css.getPropertyValue('--scan-y')),
                scanning:unit.classList.contains('scanning'),verified:unit.classList.contains('verified'),
                status:unit.querySelector('.fp-status').textContent,beamOpacity:parseFloat(beam.opacity)};
        }''',index)

    seek(6350)
    frame.wait_for_timeout(750)
    assert frame.locator('.fp-unit').count()==4
    assert frame.locator('.fp-touch').count()==4
    assert frame.locator('use[href="#tnolar-fingerprint"]').count()==8
    assert frame.locator('.lock-interact,.key-rotor,.lock-core').count()==0
    assert frame.locator('#authUnlock').inner_text()=='指 纹 认 证'
    assert frame.locator('#authUnlock').is_enabled()
    assert all(state(i)['pct']==0 for i in range(4))
    boxes=frame.evaluate('''() => {
        const button=document.querySelector('#authUnlock').getBoundingClientRect();
        const row=document.querySelector('.auth-scanners').getBoundingClientRect();
        const rects=[...document.querySelectorAll('.fp-unit')].map(el=>el.getBoundingClientRect());
        return {buttonBottom:button.bottom,scannerTop:row.top,
          columns:rects.map(r=>({x:r.x,y:r.y,width:r.width,height:r.height}))};
    }''')
    assert boxes['buttonBottom']+8<boxes['scannerTop'],boxes
    assert all(abs(v['y']-boxes['columns'][0]['y'])<1 for v in boxes['columns']), boxes
    assert all(v['height']>140 for v in boxes['columns']),boxes
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-fingerprint-idle.png'))

    # Start via individual scanner; this triggers the same four-stage cycle as
    # the primary button without asking for real fingerprints.
    frame.locator('#fp3 .fp-touch').click()
    frame.wait_for_timeout(300)
    assert state(0)['scanning']
    assert frame.locator('#authUnlock').is_disabled()
    assert not state(1)['scanning']
    assert 0<state(0)['pct']<40,state(0)

    seek(7040)
    mid=state(0)
    assert mid['scanning'] and 35<mid['pct']<85 and mid['beamOpacity']>0.5,mid
    frame.locator('body').screenshot(path=str(ROOT/'docs/preview-tnolar-fingerprint-scan.png'))
    seek(7710)
    assert state(0)['verified'] and state(0)['pct']==100 and state(0)['status']=='PASS'
    assert not state(1)['verified']
    seek(8380)
    assert state(1)['scanning'] and state(0)['verified']
    seek(10430)
    assert all(state(i)['verified'] for i in range(3))
    assert not state(3)['verified']
    seek(11790)
    assert all(state(i)['verified'] for i in range(4))

    # Replay and verify the real button-to-Ready flow also completes.
    frame.evaluate('window.DSHStartup.replay()')
    seek(6350)
    frame.locator('#authUnlock').click()
    frame.wait_for_function('document.querySelector("#stage").dataset.phase==="ready"',timeout=11000)
    assert frame.locator('.fp-unit.verified').count()==4
    frame.wait_for_selector('#readyCard',state='visible',timeout=3000)
    assert frame.locator('.ready-heading').inner_text()=='请您指挥'
    assert '等待命令输入' in frame.locator('.ready-desc').inner_text()
    assert 'INSERT' not in frame.locator('body').inner_text()
    page.wait_for_timeout(450)
    assert page.locator('#dsh-theme-tnolar-overlay').count()==1
    frame.locator('#enterButton').click()
    page.wait_for_timeout(450)
    assert page.locator('#dsh-theme-tnolar-overlay').count()==0
    assert not page.locator('#root').evaluate('(el)=>el.inert')
    assert not errors, errors
    print('Four fingerprint scan stages, accessibility, layout and host return: PASS')
    browser.close()