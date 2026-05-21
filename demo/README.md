# aspire_dash demo

Component showcase / styles gallery for every public surface in `aspire_dash`.

## Run locally

```powershell
py -3.12 -m pip install -e ..  # install the library from sibling folder
py -3.12 app.py                 # http://localhost:8060
```

## Deploy to Posit Connect

```powershell
rsconnect deploy dash . --title "aspire_dash · Component Showcase"
```

Subsequent redeploys: `rsconnect deploy dash . --app-id <guid>`.

## Page index

| Page | Module covered |
|---|---|
| `/` (home) | Overview |
| `/colours`, `/palette-lab` | `aspire_dash.theme` |
| `/kpis` | `aspire_dash.components.kpi` |
| `/cards` | `aspire_dash.components.cards` |
| `/inputs` | `aspire_dash.components.inputs` (incl. v0.10 `date_picker_single`) |
| `/feedback` | `aspire_dash.components.feedback` |
| `/skeletons` | `aspire_dash.skeletons` (incl. v0.10 `skel_sync_overlay`) |
| `/tables` | `aspire_dash.tables` (incl. v0.10 `NUMERIC_COL_DEF` + editable gotchas) |
| `/print-export` | `aspire_dash.components.print_export` (incl. v0.10 `a4_report_shell`, `register_print_button`, `safe_markdown_label`) |
| `/athlete` | `aspire_dash.athlete` |
| `/budget` | `aspire_dash.budget` |
| `/sports` | `aspire_dash.sports` |
| `/firstbeat` | `aspire_dash.firstbeat` |
| `/charts`, `/viz` | `aspire_dash.charts` + viz patterns |

## Contributing

When you add a public component to `aspire_dash`, add (or extend) the matching
page here in the same commit. The CHANGELOG should reference the demo
section so consumers can see the change live.
