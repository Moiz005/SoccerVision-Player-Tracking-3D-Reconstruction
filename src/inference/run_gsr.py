"""Custom video adapter for SoccerNet GSR pipeline.

Converts any .mp4 clip into the SoccerNet directory structure that
``SoccerNetGameState`` dataset class expects (structure mimicry).

This avoids modifying TrackLab internals — we just place frames and
metadata in the expected format so the existing loader works unchanged.
"""

import cv2
import os


def prepare_custom_video(video_path: str, output_dir: str, video_name: str) -> dict:
    """Convert a video clip into SoccerNet-compatible directory structure.

    Creates the following layout under ``output_dir``::

        output_dir/
          valid/
            video_name/
              img1/
                000001.jpg
                000002.jpg
                ...
              seqinfo.ini
              gameinfo.ini
              gt/
                gt.txt          (empty — no ground truth)

    Parameters
    ----------
    video_path : str
        Path to the input .mp4 video file.
    output_dir : str
        Root directory for the SoccerNet-compatible dataset (e.g. ``data/custom_video``).
    video_name : str
        Name for the video subdirectory (e.g. ``"my_clip"``).

    Returns
    -------
    dict
        Metadata about the processed video with keys:
        ``video_name``, ``frame_count``, ``fps``, ``width``, ``height``,
        ``output_path`` — the created SoccerNet directory path.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cap.release()

    if frame_count == 0:
        raise ValueError(f"Video {video_path} contains 0 frames")

    # ── 1. Create directory structure ──────────────────────────────────
    valid_dir = os.path.join(output_dir, "valid")
    video_dir = os.path.join(valid_dir, video_name)
    img1_dir = os.path.join(video_dir, "img1")
    gt_dir = os.path.join(video_dir, "gt")

    os.makedirs(img1_dir, exist_ok=True)
    os.makedirs(gt_dir, exist_ok=True)

    # ── 2. Extract all frames ──────────────────────────────────────────
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(img1_dir, f"{frame_idx + 1:06d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_idx += 1
    cap.release()

    extracted = frame_idx
    assert extracted == frame_count, (
        f"Extracted {extracted} frames but expected {frame_count} from video metadata"
    )

    # ── 3. Write seqinfo.ini ───────────────────────────────────────────
    seqinfo_path = os.path.join(video_dir, "seqinfo.ini")
    with open(seqinfo_path, "w") as f:
        f.write("[Sequence]\n")
        f.write(f"name={video_name}\n")
        f.write(f"imDir=img1\n")
        f.write(f"frameRate={fps:.2f}\n")
        f.write(f"seqLength={frame_count}\n")
        f.write(f"imWidth={width}\n")
        f.write(f"imHeight={height}\n")
        f.write(f"imExt=.jpg\n")

    # ── 4. Write gameinfo.ini (placeholders) ───────────────────────────
    gameinfo_path = os.path.join(video_dir, "gameinfo.ini")
    with open(gameinfo_path, "w") as f:
        f.write("[Game]\n")
        f.write(f"name={video_name}\n")
        f.write("team_home=Home\n")
        f.write("team_away=Away\n")
        f.write("stadium=Unknown\n")
        f.write("city=Unknown\n")
        f.write("competition=Custom\n")
        f.write("season=2026\n")

    # ── 5. Write empty gt.txt ──────────────────────────────────────────
    gt_path = os.path.join(gt_dir, "gt.txt")
    with open(gt_path, "w") as f:
        pass  # empty file — required by SoccerNetGameState loader

    return {
        "video_name": video_name,
        "frame_count": frame_count,
        "fps": round(fps, 2),
        "width": width,
        "height": height,
        "output_path": video_dir,
    }


def print_video_info(video_path: str) -> dict:
    """Print and return metadata for a video file without extracting frames.

    Useful for quick inspection.

    Parameters
    ----------
    video_path : str
        Path to a video file.

    Returns
    -------
    dict
        Keys: ``video_path``, ``fps``, ``width``, ``height``, ``frame_count``.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {video_path}")

    info = {
        "video_path": video_path,
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }
    cap.release()

    print(f"Video:      {video_path}")
    print(f"Frames:     {info['frame_count']}")
    print(f"FPS:        {info['fps']:.2f}")
    print(f"Resolution: {info['width']}x{info['height']}")
    return info


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python run_gsr.py <video_path> <output_dir> <video_name>")
        print("Example: python run_gsr.py match_clip.mp4 data/custom_video my_clip")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    video_name = sys.argv[3]

    print(f"Preparing custom video: {video_path}")
    print(f"Output root:            {output_dir}")
    print(f"Video name:             {video_name}")

    meta = prepare_custom_video(video_path, output_dir, video_name)
    print("\n✅ Video adapter complete!")
    print(f"   Frames extracted: {meta['frame_count']}")
    print(f"   FPS:              {meta['fps']}")
    print(f"   Resolution:       {meta['width']}x{meta['height']}")
    print(f"   Output path:      {meta['output_path']}")
    print(f"   Structure:")
    for root, dirs, files in os.walk(meta["output_path"]):
        level = root.replace(meta["output_path"], "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = " " * 4 * (level + 1)
        for file in files:
            print(f"{sub_indent}{file}")
