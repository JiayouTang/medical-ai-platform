# Frontend

Phase-1 demo frontend using React + Vite + MUI + ECharts.

This follows the mature workbench direction from `third_party/data-formulator`: dense app shell, schema browser, query/result workspace, and execution detail panel. It does not copy the full Data Formulator app because that would bring Redux persistence, auth, data connectors, editors, and broad visualization workflow before this project needs them.

## Run

Start the backend API from the project root:

```bash
conda run -n medical-ai python scripts/run_demo_server.py --host 127.0.0.1 --port 8000
```

Start the Vite dev server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Build

```bash
npm run build
```

After a successful build, `scripts/run_demo_server.py` can also serve `frontend/dist` directly.
