import re, xml.etree.ElementTree as ET, collections
p='source_map.svg'
s=open(p,encoding='utf-8').read()
style=re.search(r'<style>(.*?)</style>',s,re.S).group(1)
props=collections.defaultdict(dict)
for selectors,body in re.findall(r'([^{}]+)\{([^{}]+)\}',style):
    d={k.strip():v.strip() for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',body)}
    for cls in re.findall(r'\.([\w-]+)',selectors): props[cls].update(d)
root=ET.parse(p).getroot(); counts=collections.Counter(); types=collections.defaultdict(collections.Counter)
for el in root.iter():
    cls=el.attrib.get('class','')
    for c in cls.split(): counts[c]+=1;types[c][el.tag.rsplit('}',1)[-1]]+=1
rows=[]
for c,d in props.items():
    if d.get('stroke') and d.get('stroke') not in ('#fff','#000') and counts[c]:
      rows.append((c,d.get('stroke'),d.get('stroke-width'),d.get('fill'),counts[c],dict(types[c])))
for r in sorted(rows,key=lambda x:x[1]):print(*r,sep=' | ')
