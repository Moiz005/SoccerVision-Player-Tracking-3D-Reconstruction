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

```python
# Cell 1: Clone repo and install
!git clone https://github.com/<user>/<repo>.git
%cd <repo>
!pip install -r requirements_colab.txt

# Cell 2: Clone sn-gamestate and install
!git clone https://github.com/SoccerNet/sn-gamestate.git
!git clone https://github.com/TrackingLaboratory/tracklab.git
%cd sn-gamestate
!pip install -e .
!pip install mim
!mim install mmcv==2.0.1

# Cell 3: Run baseline
!tracklab -cn soccernet
```

## Local Development (analysis only, no GPU needed)

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## References

- **SoccerNet GSR Paper:** [Game State Reconstruction](https://github.com/SoccerNet/sn-gamestate)
- **sn-gamestate Repo:** https://github.com/SoccerNet/sn-gamestate
- **TrackLab Framework:** https://github.com/TrackingLaboratory/tracklab
- **SoccerNet Dataset:** https://soccer-net.org/

## License

This project evaluates and extends the SoccerNet GSR baseline (GPL-3.0). See individual dependency licenses for details.
