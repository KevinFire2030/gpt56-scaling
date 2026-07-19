from pathlib import Path
import shutil
from comtypes.client import CreateObject

src = Path('deck.pptx').resolve()
out = Path('preview').resolve()
if out.exists(): shutil.rmtree(out)
out.mkdir()
app = CreateObject('PowerPoint.Application')
pres = None
try:
    app.Visible = 1
    pres = app.Presentations.Open(str(src), False, False, False)
    pres.SaveAs(str(out), 18)  # ppSaveAsPNG
    pres.Close()
    pres = None
finally:
    if pres is not None:
        pres.Close()
    app.Quit()
files = sorted(list(out.glob('*.PNG')) + list(out.glob('*.png')))
print(f'Rendered {len(files)} PNG previews to {out}')
for f in files: print(f.name)
