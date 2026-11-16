"""Preview the assembled site; the original section preview is preserved."""
from pathlib import Path
from types import SimpleNamespace
import build_site
import render_preview

HERE=Path(__file__).resolve().parent
blocks,_=build_site.read_template(HERE/'abandoned_drill_camp.nbt')
render_preview.scene=SimpleNamespace(blocks=blocks,SIZE=build_site.SIZE)
render_preview.render(HERE/'abandoned_drill_camp_preview.png',title='ABANDONED DRILL CAMP',
    subtitle='96 x 96 site | Hasla crafting pavilion + three 48 x 48 habitat sections | block-layout preview')
render_preview.render(HERE/'abandoned_drill_camp_overview.png',overhead=True,title='ABANDONED DRILL CAMP',
    subtitle='Four connected sections | shallow water and open roaming routes | block-layout preview')
