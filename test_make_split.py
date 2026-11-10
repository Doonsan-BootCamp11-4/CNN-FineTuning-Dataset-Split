"""make_split 자체 검증: 실제 데이터 없이 가짜 폴더로 split 규칙을 확인한다.

실행: python test_make_split.py  (또는 python -m pytest)
"""
import tempfile
from collections import Counter
from pathlib import Path

from make_split import make_split


def test_split_ratio_and_determinism() -> None:
    # 임시 폴더에 root/<class>/<image> 구조를 흉내 낸다 (테스트 끝나면 자동 삭제)
    with tempfile.TemporaryDirectory() as d: # 임시 os의 temp 파일 생성
        # 클래스 a는 100장(비율 계산이 딱 떨어짐), b는 37장(반올림 경계 확인용)
        for cls, n in [("a", 100), ("b", 37)]:
            (Path(d) / cls).mkdir()
            for i in range(n):
                (Path(d) / cls / f"{i}.jpg").touch()  # 내용이 있으면 수정 x, 내용 없는 빈 파일이면 충분
        (Path(d) / "a" / "note.txt").touch()  # 이미지 확장자가 아니므로 제외되어야 함

        rows = make_split(d)

        # 모든 이미지가 빠짐없이 포함되고, txt 파일은 빠졌는지
        assert len(rows) == 137
        # 같은 이미지가 두 split에 들어가지 않았는지 (데이터 누수 방지)
        assert len({r[0] for r in rows}) == 137
        # 클래스별로 60/20/20 비율이 지켜졌는지
        assert Counter(r[2] for r in rows if r[1] == "a") == {"train": 60, "val": 20, "test": 20}
        # 같은 seed로 다시 돌리면 결과가 완전히 같은지 (다른 팀과 같은 split 보장)
        assert rows == make_split(d)
        # seed를 바꾸면 결과가 달라지는지 (seed가 실제로 쓰이는지)
        assert rows != make_split(d, seed=1)


if __name__ == "__main__":
    # pytest 없이 python으로 바로 실행할 때
    test_split_ratio_and_determinism()
    print("ok")
