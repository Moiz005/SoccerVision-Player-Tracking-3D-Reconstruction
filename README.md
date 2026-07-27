# SoccerVision — Player Tracking & 3D Reconstruction

Run the official [SoccerNet Game State Reconstruction (GSR)](https://github.com/SoccerNet/sn-gamestate) baseline on arbitrary football broadcast clips, evaluate its output quality, and produce standardized tracking data (JSON/CSV) for downstream 3D reconstruction in Blender.

## Project Structure

```
├── notebooks/          # Colab entry points
├── src/
│   ├── inference/      # SoccerNet GSR pipeline wrappers
│   ├── processing/     # Tracker state parsing
│   ├── export/         # JSON/CSV export
│   └── visualization/  # Debug overlays & pitch minimaps
├── configs/            # Hydra YAML configs
├── samples/            # Short test clips (<10 MB, gitignored)
└── outputs/            # Inference outputs (gitignored)
```

## Development Workflow

```
Local (OpenCode)              GitHub              Colab (GPU)
──────────────────         ─────────────         ──────────────
Write code/scripts    →   Push         →   Pull repo
Create notebook            ↑                    ↓
Modify configs         ←   Results    ←   Run inference
Analyze outputs               ↑                    ↓
                           Download          GPU inference
                           results           Save outputs
```

1. **Local:** Write code, configs, and notebooks here.
2. **Push** to GitHub when ready.
3. **Colab:** Clone the repo, install dependencies, and run inference on a GPU.

## Quick Start (Colab)

Open the notebook directly in Colab from GitHub:

```
https://colab.research.google.com/github/Moiz005/SoccerVision-Player-Tracking-3D-Reconstruction/blob/main/notebooks/inference_colab.ipynb
```

> **Note:** Colab aggressively caches GitHub notebooks. If the notebook shows an old version after you push updates, add a cache-buster to the URL:
> ```
> https://colab.research.google.com/github/Moiz005/SoccerVision-Player-Tracking-3D-Reconstruction/blob/main/notebooks/inference_colab.ipynb?t=1
> ```
> Increment the `?t=` number each time you push changes. Alternatively, close the Colab tab entirely and open the URL fresh.

## Local Development (analysis only, no GPU needed)

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Pipeline Stages

The GSR baseline runs 9 pipeline stages in sequence. On Colab, jersey number detection is **skipped** due to mmcv incompatibility.

| # | Stage | Module | Description | Colab |
|---|-------|--------|-------------|-------|
| 1 | `bbox_detector` | YOLOv11 (Ultralytics) | Detects player & ball bounding boxes per frame | ✅ |
| 2 | `reid` | PRTReid | Extracts appearance embeddings for re-identification | ✅ |
| 3 | `track` | StrongSORT + BPBreid | Multi-object tracking with Re-ID association | ✅ |
| 4 | `pitch` | NBW calibration | Detects pitch lines/corners for homography | ✅ |
| 5 | `calibration` | NBW calibration | Maps pixel coordinates to real-world pitch coordinates | ✅ |
| 6 | `jersey_number_detect` | MMOCR | Reads jersey numbers from player crops | ❌ Skipped |
| 7 | `tracklet_agg` | Voting + jersey numbers | Aggregates tracklets, assigns roles (GK, player) | ✅ |
| 8 | `team` | K-means on embeddings | Clusters players into two teams by appearance | ✅ |
| 9 | `team_side` | Mean position | Determines which team is attacking left/right | ✅ |

### Why jersey number detection is skipped

MMOCR depends on mmcv, which has no pre-built wheels for Colab's Python 3.12 + torch 2.x. Building from source takes too long. The pipeline runs without it by excluding the module:

```bash
!tracklab -cn soccernet \
    ~modules.jersey_number_detect \
    pipeline='[bbox_detector,reid,track,pitch,calibration,tracklet_agg,team,team_side]'
```

**Impact:** Without jersey numbers, the `tracklet_agg` stage uses only appearance embeddings (no number-based disambiguation). Team assignment via K-means still works. This is acceptable for initial testing.

## References

- **SoccerNet GSR Paper:** [Game State Reconstruction](https://github.com/SoccerNet/sn-gamestate)
- **sn-gamestate Repo:** https://github.com/SoccerNet/sn-gamestate
- **TrackLab Framework:** https://github.com/TrackingLaboratory/tracklab
- **SoccerNet Dataset:** https://soccer-net.org/

## License

This project evaluates and extends the SoccerNet GSR baseline (GPL-3.0). See individual dependency licenses for details.
