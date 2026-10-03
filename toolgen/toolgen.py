#!/usr/bin/env python3
# PixHarvest 免费工具矩阵扩产生成器
import os, sys, html, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topics import TOPICS

SITE = 'https://contentforge-press.github.io'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

CSS = """
:root{--brand:#0b4da2;--brand-d:#083a7d;--ink:#1f2937;--mut:#6b7280;--line:#e5e7eb;--bg:#f8fafc;--card:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}
.wrap{max-width:960px;margin:0 auto;padding:0 20px}
header{background:var(--brand);color:#fff;padding:14px 0}
.brand{font-weight:700;font-size:17px;letter-spacing:.2px}
.brand a{color:#fff;text-decoration:none}
.brand small{opacity:.85;font-weight:400;margin-left:10px}
.hero{padding:34px 0 10px}
h1{font-size:28px;line-height:1.3;color:var(--ink)}
.sub{color:var(--mut);font-size:15px;margin-top:8px}
.calc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px;margin:22px 0}
.calc label{display:block;font-weight:600;font-size:14px;margin:12px 0 6px}
.calc input{width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;font-size:15px}
.calc button{margin-top:16px;padding:11px 22px;background:var(--brand);color:#fff;border:none;border-radius:8px;font-size:15px;cursor:pointer;font-weight:600}
.calc button:hover{background:var(--brand-d)}
.result{margin-top:16px;padding:14px;border-radius:8px;background:#f0f7ff;border:1px solid #bcd9f5;font-size:15px;display:none}
.result b{color:var(--brand)}
.sec h2{font-size:21px;margin:28px 0 10px}
.sec p{color:#374151;margin-bottom:10px}
.related{margin:26px 0;padding:16px;background:var(--card);border:1px solid var(--line);border-radius:12px}
.related h3{font-size:15px;margin-bottom:10px}
.related a{display:inline-block;margin:4px 10px 4px 0;color:var(--brand);text-decoration:none;font-size:14px}
footer{margin-top:40px;padding:22px 0;border-top:1px solid var(--line);color:var(--mut);font-size:13px;background:var(--card)}
footer a{color:var(--brand);text-decoration:none}
.pill{display:inline-block;background:#eef4ff;color:var(--brand);border-radius:999px;padding:2px 12px;font-size:12px;font-weight:600;margin-top:10px}
@media(max-width:640px){h1{font-size:22px}}
"""

# ---------- 公式 JS 模板 ----------
def formula_js(f_type, p):
    f = p.get('fixed', 0); pct = p.get('pct', 0); rate = p.get('rate', 0)
    cat = html.escape(p.get('cat',''))
    if f_type == 'fee_pct_fixed':
        return f"""
const pr=+i1.value||0, f1=pr*{pct}, f2={f}, fee=f1+f2, net=pr-fee;
o.style.display='block';
o.innerHTML='Fee: <b>$'+fee.toFixed(2)+'</b> ('+({pct*100}).toFixed(1)+'% + $'+({f}).toFixed(2)+') &nbsp;·&nbsp; Net: <b>$'+net.toFixed(2)+'</b>';"""
    if f_type == 'flat_fee':
        return f"""
const pr=+i1.value||0, fee={f}, net=pr-fee;
o.style.display='block';
o.innerHTML='Fee: <b>$'+fee.toFixed(2)+'</b> &nbsp;·&nbsp; Net: <b>$'+net.toFixed(2)+'</b>';"""
    if f_type == 'sales_tax':
        return f"""
const pr=+i1.value||0, tax=pr*{rate}, total=pr+tax;
o.style.display='block';
o.innerHTML='Tax: <b>$'+tax.toFixed(2)+'</b> &nbsp;·&nbsp; Total: <b>$'+total.toFixed(2)+'</b>';"""
    if f_type == 'vat':
        return f"""
const pr=+i1.value||0, vat=pr*{rate}, gross=pr+vat, net=pr/(1+{rate});
o.style.display='block';
o.innerHTML='VAT: <b>$'+vat.toFixed(2)+'</b> &nbsp;·&nbsp; Gross: <b>$'+gross.toFixed(2)+'</b> &nbsp;·&nbsp; Net (remove VAT): <b>$'+net.toFixed(2)+'</b>';"""
    if f_type == 'gst':
        return f"""
const pr=+i1.value||0, gst=pr*{rate}, gross=pr+gst, net=pr/(1+{rate});
o.style.display='block';
o.innerHTML='GST: <b>$'+gst.toFixed(2)+'</b> &nbsp;·&nbsp; Gross: <b>$'+gross.toFixed(2)+'</b> &nbsp;·&nbsp; Net (excl): <b>$'+net.toFixed(2)+'</b>';"""
    if f_type == 'tariff':
        return f"""
const v=+i1.value||0, duty=v*{rate}, mf=Math.max(2.50,v*0.003464), total=duty+mf;
o.style.display='block';
o.innerHTML='Duty: <b>$'+duty.toFixed(2)+'</b> &nbsp;·&nbsp; MPF/processing: <b>$'+mf.toFixed(2)+'</b> &nbsp;·&nbsp; Total fees: <b>$'+total.toFixed(2)+'</b>';"""
    if f_type == 'margin':
        return f"""
const pr=+i1.value||0, co=+i2.value||0, g=pr-co, gm=pr>0?(g/pr*100):0;
o.style.display='block';
o.innerHTML='Gross profit: <b>$'+g.toFixed(2)+'</b> &nbsp;·&nbsp; Margin: <b>'+gm.toFixed(1)+'%</b>';"""
    if f_type == 'markup':
        return f"""
const co=+i1.value||0, mu=+i2.value||0, pr=co*(1+mu/100), g=pr-co;
o.style.display='block';
o.innerHTML='Selling price: <b>$'+pr.toFixed(2)+'</b> &nbsp;·&nbsp; Profit: <b>$'+g.toFixed(2)+'</b>';"""
    if f_type == 'roas':
        return f"""
const rev=+i1.value||0, ad=+i2.value||0, ro=ad>0?(rev/ad):0;
o.style.display='block';
o.innerHTML='ROAS: <b>'+ro.toFixed(2)+'x</b> &nbsp;·&nbsp; '+ (ro>=3?'Healthy (>3x)':ro>=1?'Breaking even-ish':'Below 1x — check targeting');"""
    if f_type == 'acos':
        return f"""
const rev=+i1.value||0, ad=+i2.value||0, ac=rev>0?(ad/rev*100):0;
o.style.display='block';
o.innerHTML='ACoS: <b>'+ac.toFixed(1)+'%</b> &nbsp;·&nbsp; Spend: <b>$'+ad.toFixed(2)+'</b> on $'+rev.toFixed(2)+' revenue';"""
    if f_type == 'breakeven':
        return f"""
const fx=+i1.value||0, vc=+i2.value||0, cm=fx>0&&vc>0?(fx/vc):0;
o.style.display='block';
o.innerHTML='Break-even units: <b>'+cm.toFixed(0)+'</b> &nbsp;·&nbsp; Break-even revenue: <b>$'+(cm*(+i2.value||0)).toFixed(2)+'</b> (fixed ÷ contribution per unit)';"""
    if f_type == 'shipping':
        return f"""
const w=+i1.value||0, z=+i2.value||0, base=4.5+ w*0.85 + z*0.35;
o.style.display='block';
o.innerHTML='Est. shipping: <b>$'+base.toFixed(2)+'</b> &nbsp;·&nbsp; (weight '+w+' lb · zone '+z+')';"""
    if f_type == 'discount':
        return f"""
const pr=+i1.value||0, d=+i2.value||0, sale=pr*(1-d/100);
o.style.display='block';
o.innerHTML='Sale price: <b>$'+sale.toFixed(2)+'</b> &nbsp;·&nbsp; Discount: <b>$'+(pr-sale).toFixed(2)+'</b> ('+d+'%)';"""
    if f_type == 'ltv':
        return f"""
const aov=+i1.value||0, fr=+i2.value||0, lt=36, ltv=aov*fr*(lt/12);
o.style.display='block';
o.innerHTML='LTV (36-mo model): <b>$'+ltv.toFixed(2)+'</b> &nbsp;·&nbsp; (AOV $'+aov.toFixed(2)+' × '+fr.toFixed(1)+' orders/mo × 36 mo)';"""
    if f_type == 'turnover':
        return f"""
const cogs=+i1.value||0, inv=+i2.value||0, to=inv>0?(cogs/inv):0, doh=to>0?(365/to):0;
o.style.display='block';
o.innerHTML='Turnover: <b>'+to.toFixed(1)+'x</b> &nbsp;·&nbsp; Days on hand: <b>'+doh.toFixed(0)+'</b>';"""
    if f_type == 'restock':
        return f"""
const dd=+i1.value||0, lt=+i2.value||0, ss=dd*0.5*1.65, rop=dd*lt+ss;
o.style.display='block';
o.innerHTML='Reorder point: <b>'+rop.toFixed(1)+' units</b> &nbsp;·&nbsp; Safety stock: <b>'+ss.toFixed(1)+'</b>';"""
    if f_type == 'compare':
        return f"""
const pr=+i1.value||0, a=pr*{pct}+{f}, b=pr*0.10+0.30, keepA=pr-a, keepB=pr-b;
o.style.display='block';
o.innerHTML='Platform A: keep <b>$'+keepA.toFixed(2)+'</b> (fee $'+a.toFixed(2)+') · Platform B: keep <b>$'+keepB.toFixed(2)+'</b> (fee $'+b.toFixed(2)+')';"""
    return f"""
const pr=+i1.value||0, fee=pr*{pct}+{f}, net=pr-fee;
o.style.display='block';
o.innerHTML='Fee: <b>$'+fee.toFixed(2)+'</b> · Net: <b>$'+net.toFixed(2)+'</b>';"""

def inputs_html(f_type):
    if f_type in ('margin', 'markup', 'roas', 'acos'):
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">Sale price / Revenue ($)</label><input id="i1" placeholder="100.00"></div>'
                '<div><label for="i2">' + ('Cost ($)</label><input id="i2" placeholder="60.00">' if f_type=='margin' else 'Markup %</label><input id="i2" placeholder="50">' if f_type=='markup' else 'Ad spend ($)</label><input id="i2" placeholder="20.00">') + '</div></div>')
    if f_type == 'breakeven':
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">Fixed costs ($/mo)</label><input id="i1" placeholder="2000"></div>'
                '<div><label for="i2">Contribution per unit ($)</label><input id="i2" placeholder="15.00"></div></div>')
    if f_type == 'shipping':
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">Weight (lb)</label><input id="i1" placeholder="2"></div>'
                '<div><label for="i2">Zone</label><input id="i2" placeholder="5"></div></div>')
    if f_type == 'discount':
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">Original price ($)</label><input id="i1" placeholder="80.00"></div>'
                '<div><label for="i2">Discount %</label><input id="i2" placeholder="20"></div></div>')
    if f_type == 'ltv':
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">Average order value ($)</label><input id="i1" placeholder="45.00"></div>'
                '<div><label for="i2">Orders per month</label><input id="i2" placeholder="1.5"></div></div>')
    if f_type == 'turnover':
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">COGS ($/yr)</label><input id="i1" placeholder="120000"></div>'
                '<div><label for="i2">Average inventory ($)</label><input id="i2" placeholder="20000"></div></div>')
    if f_type == 'restock':
        return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label for="i1">Daily demand (units)</label><input id="i1" placeholder="10"></div>'
                '<div><label for="i2">Lead time (days)</label><input id="i2" placeholder="7"></div></div>')
    return '<div><label for="i1">Amount / Sale price ($)</label><input id="i1" placeholder="100.00"></div>'

def build_page(slug, title, desc, f_type, p):
    cat = html.escape(p.get('cat', ''))
    cal_js = formula_js(f_type, p)
    body = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}/{slug}.html">
<style>{CSS}</style></head><body>
<header><div class="wrap"><div class="brand"><a href="/index.html">PixHarvest Tools</a><small>free seller calculators · 2026</small></div></div></header>
<div class="wrap">
<div class="hero"><span class="pill">{cat}</span>
<h1>{html.escape(title)}</h1>
<p class="sub">{html.escape(desc)}</p></div>
<div class="calc">
{inputs_html(f_type)}
<button onclick="go()">Calculate</button>
<div class="result" id="o"></div>
</div>
<div class="sec">
<h2>How to use this calculator</h2>
<p>Enter the {('sale price and cost' if f_type=='margin' else 'amount')} above and click <b>Calculate</b>. The result shows the {'fee and net payout' if f_type in ('fee_pct_fixed','flat_fee','compare') else 'tax and total' if f_type in ('sales_tax','vat','gst') else 'duty and processing fees' if f_type=='tariff' else 'profit and margin' if f_type=='margin' else 'selling price and profit' if f_type=='markup' else 'return on ad spend' if f_type=='roas' else 'advertising cost of sales' if f_type=='acos' else 'break-even units' if f_type=='breakeven' else 'shipping estimate' if f_type=='shipping' else 'sale price and discount' if f_type=='discount' else 'customer lifetime value' if f_type=='ltv' else 'inventory efficiency' if f_type=='turnover' else 'reorder point'}.</p>
<p>Fee structures change — always confirm the current rate on the platform's own fee page before final pricing decisions.</p>
</div>
<div class="related"><h3>Related tools</h3>
<a href="/amazon-fba-calculator.html">Amazon FBA calculator</a><a href="/ebay-calculator.html">eBay calculator</a><a href="/etsy-fee-calculator-2026.html">Etsy calculator</a><a href="/shopify-profit-calculator.html">Shopify calculator</a><a href="/paypal-fee-calculator.html">PayPal calculator</a><a href="/tools.html">All 400+ tools</a>
</div>
</div>
<footer><div class="wrap">
<p>PixHarvest — live data APIs for AI agents &amp; sellers: <a href="https://pixharvest.com/try">free Shopify/GitHub/App Store/HN/job-intel snapshots</a>.</p>
<p style="margin:0;">Free live snapshot &rarr; <a href="https://pixharvest.com/try">pixharvest.com/try</a></p>
</div></footer>
<script>
function go(){{var o=document.getElementById('o');var i1=document.getElementById('i1');var i2=document.getElementById('i2')||{{value:0}};
{cal_js}
}}
</script>
</body></html>"""
    return body

def main():
    count = 0
    for slug, title, desc, f_type, p in TOPICS:
        page = build_page(slug, title, desc, f_type, p)
        path = os.path.join(OUT, slug + '.html')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(page)
        count += 1
    print(f'生成 {count} 个工具页')

if __name__ == '__main__':
    main()
