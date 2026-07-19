import xml.etree.ElementTree as ET
r=ET.parse('source_map.svg').getroot();i=0
for e in r.iter():
 if e.attrib.get('class')=='cls-53':
  i+=1; print(i,e.tag.rsplit('}',1)[-1],e.attrib)
