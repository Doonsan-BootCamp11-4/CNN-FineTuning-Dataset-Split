"""Garbage Classification(12클래스)을 클래스별 비율을 유지해 train/val/test로 나눠 CSV로 저장한다.

사용 (Kaggle):
    !python make_split.py --root /kaggle/input/garbage-classification/garbage_classification
"""
import argparse
import csv
import random
from collections import Counter
from pathlib import Path

EXTS = {".jpg", ".jpeg", ".png"}


def make_split(
    root: str | Path, seed: int = 42, train: float = 0.6, val: float = 0.2
) -> list[tuple[str, str, str]]:
    """root/<class>/<image> 구조를 읽어 (path, label, split) 행 목록을 돌려준다. path는 root 기준 상대 경로."""
    root = Path(root)
    rows = []
    for cls_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        # 정렬 후 셔플해야 OS/파일시스템과 무관하게 같은 split이 나온다
        files = sorted(p.relative_to(root).as_posix() for p in cls_dir.iterdir() if p.suffix.lower() in EXTS)
        random.Random(seed).shuffle(files)
        n_train = round(len(files) * train)
        n_val = round(len(files) * val)
        for i, f in enumerate(files):
            split = "train" if i < n_train else "val" if i < n_train + n_val else "test"
            rows.append((f, cls_dir.name, split))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="../splits_datasets.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = Path(args.out)
    if out.exists():
        # 이미 만든 split을 덮어쓰면 다른 팀과 split이 어긋날 수 있으므로 건너뛴다
        print(f"{out} already exists, skip")
        return

    rows = make_split(args.root, args.seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "label", "split"])
        w.writerows(rows)

    print(f"{len(rows)} images, {len({r[1] for r in rows})} classes -> {out}")
    print(dict(Counter(r[2] for r in rows)))


if __name__ == "__main__":
    main()
