from pathlib import Path

def test_package_has_single_responsibility_layout():
 root=Path(__file__).parents[1]/"genesis"
 expected={"core","domain","work","agents","knowledge","platform","world","runtime"}
 assert expected <= {p.name for p in root.iterdir() if p.is_dir()}
 assert not any((root/x).exists() for x in ("agent.py","database.py","policy.py","treasury.py","tasks.py","tools.py"))

def test_runtime_data_is_not_source_data():
 assert not (Path(__file__).parents[1]/"workspace").exists()
