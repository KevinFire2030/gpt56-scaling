import re,xml.etree.ElementTree as ET,collections
s=open('source_map.svg',encoding='utf-8').read();style=re.search(r'<style>(.*?)</style>',s,re.S).group(1);props=collections.defaultdict(dict)
for sels,body in re.findall(r'([^{}]+)\{([^{}]+)\}',style):
 d={k.strip():v.strip() for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',body)}
 for c in re.findall(r'\.([\w-]+)',sels):props[c].update(d)
r=ET.parse('source_map.svg').getroot();ct=collections.Counter()
for e in r.iter():
 if e.tag.endswith(('circle','ellipse')): ct[e.attrib.get('class','')]+=1
for c,n in ct.most_common(): print(c,n,props.get(c,{}))
