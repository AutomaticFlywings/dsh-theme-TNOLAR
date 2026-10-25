"""Computed-color + geometry regression against real DSH CSS-module names.

This fixture deliberately starts with light DSH code/chrome tokens to reproduce
TNOLAR's screenshots. It is a host mock, not an installed-DSH integration test.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
FIXTURE=(ROOT/'test/fixture-theme-contrast.html').read_text(encoding='utf8')
PLUGIN=(ROOT/'lib/client.js').read_text(encoding='utf8')

def rgb_tuple(css):
    assert css.startswith('rgb('), css
    return tuple(int(float(s.strip())) for s in css[4:-1].split(','))

def lum(rgb):
    channels=[c/255 for c in rgb]
    rr=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in channels]
    return .2126*rr[0]+.7152*rr[1]+.0722*rr[2]

def contrast(a,b):
    a,b=sorted((lum(rgb_tuple(a)),lum(rgb_tuple(b))),reverse=True)
    return round((a+.05)/(b+.05),2)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':900})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(FIXTURE)
    initial=page.evaluate('''() => {
      const tab=document.querySelector('#tab-active');const list=document.querySelector('[role=tablist]');
      const take=r=>({x:r.x,y:r.y,width:r.width,height:r.height});
      return {tab:take(tab.getBoundingClientRect()),list:take(list.getBoundingClientRect())};
    }''')
    page.evaluate("() => {window.__ModuleLoader__={load(v){window._registered=v}}}")
    page.add_script_tag(content=PLUGIN)
    page.evaluate("() => window._registered.factory(()=>{throw Error('Unexpected dependency')}).apply({effect(fn){window._cleanup=fn()}})")
    page.evaluate('window.DSHTNOLAR.skip()')
    page.wait_for_timeout(370)
    results=page.evaluate('''() => {
      const css = selector => getComputedStyle(document.querySelector(selector));
      const rect = el => {const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
      return {
        code:{bg:css('#inline-code').backgroundColor,color:css('#inline-code').color},
        codeBlock:{bg:css('#code-block').backgroundColor,color:css('#code-block').color},
        add:{bg:css('#add-button').backgroundColor,color:css('#add-button').color,opacity:css('#add-button').opacity},
        addSvg:{pathFill:css('#add-button svg path').fill,pathStroke:css('#add-button svg path').stroke},
        disabled:{bg:css('#send-disabled').backgroundColor,color:css('#send-disabled').color,opacity:css('#send-disabled').opacity},
        enabled:{bg:css('#send-enabled').backgroundColor,color:css('#send-enabled').color,opacity:css('#send-enabled').opacity},
        menu:{bg:css('#menu').backgroundColor,color:css('#menu').color},
        tab:rect(document.querySelector('#tab-active')),list:rect(document.querySelector('[role=tablist]')),
        tabAfterBg:getComputedStyle(document.querySelector('#tab-active'),'::after').backgroundColor,
        markdownToken:css('#root').getPropertyValue('--dsw-alias-markdown-inline-code').trim(),
        shikiComment:css('#root').getPropertyValue('--shiki-token-comment').trim(),
      };
    }''')
    pairs={k:contrast(results[k]['color'],results[k]['bg']) for k in ['code','codeBlock','add','disabled','enabled','menu']}
    results['ratios']=pairs
    assert all(pairs[k]>=4.5 for k in ['code','codeBlock','add','enabled','menu']),pairs
    assert pairs['disabled']>=4.5,pairs
    assert results['addSvg']['pathFill']=='none',results['addSvg']
    assert results['addSvg']['pathStroke']!='none',results['addSvg']
    assert results['disabled']['opacity']=='1',results['disabled']
    for id in ['tab','list']:
      for k in ['x','y','width','height']:
        assert abs(initial[id][k]-results[id][k])<.5,(id,k,initial,results)
    assert results['tabAfterBg']!='rgba(0, 0, 0, 0)',results['tabAfterBg']
    assert results['shikiComment']=='#a4b7c0',results['shikiComment']
    assert not errors,errors
    page.screenshot(path=str(ROOT/'docs/preview-tnolar-contrast.png'),full_page=True)
    page.evaluate('window.DSHTNOLAR.setThemeEnabled(false)')
    after=page.evaluate("() => getComputedStyle(document.querySelector('#inline-code')).backgroundColor")
    assert after=='rgb(248, 249, 250)',after
    page.evaluate('window._cleanup()')
    browser.close()
    print(json.dumps(results,ensure_ascii=False,indent=2))
    print('Color, icon-fill, tab geometry and rollback tests: PASS')