# victory-runs

A shared, public record of [VIctory](https://github.com/Marvisak/VIctory) runs (GTA VI, Xbox Series, on PC): which hardware, build and settings got how far, at what frame rate, and with which failures.

## Read it

[`data/runs.jsonl`](data/runs.jsonl) holds one JSON record per line. Use it from anything, scripts and AI models included:

```
https://raw.githubusercontent.com/shawshanker18/victory-runs/main/data/runs.jsonl
```

Or summarised by GPU and settings, with [victory-doctor](https://github.com/shawshanker18/victory-doctor):

```
python victory_doctor.py stats
python victory_doctor.py stats --gpu 4060 --setting VICTORY_RELAY
```

## Add your runs

```
python victory_doctor.py run -- target\release\victory.exe run <game dir>\<title exe> --execute
python victory_doctor.py submit <run id>
```

`submit` opens a "[run]" issue here with the record filled in. When you submit it, it is checked and added to `data/runs.jsonl` automatically, and the issue is closed.

## What a record holds

| Field | Contents |
|---|---|
| `machine` | OS, CPU, GPUs with driver versions, RAM |
| `emulator` | title build, console mode, which build or fork |
| `settings` | every `VICTORY_*` setting of the run |
| `performance` | how far it got (`boot`, `menus`, `world`); in the world: median, 10th and 90th percentile fps, ms/frame, GPU ms, draws per frame |
| `failures` | each failure's signature, how often, and whether it was new, known or fixed |

No game data, user names, folders or computer names.

## Licence

The data is CC0: use it for anything.
