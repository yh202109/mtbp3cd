import os
import tempfile
import shutil
import pandas as pd
import pytest
from mtbp3cd.util.lsr import LsrTree
import hashlib
from io import StringIO

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

def create_files_structure(base_dir):
    os.makedirs(os.path.join(base_dir, "folder1"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "folder2/empty_folder"), exist_ok=True)
    with open(os.path.join(base_dir, "file1.txt"), "w") as f:
        f.write("hello world")
    with open(os.path.join(base_dir, "folder1", "file2.txt"), "w") as f:
        f.write("another file")
    # empty folder2/empty_folder

def test_list_files_list(temp_dir):
    create_files_structure(temp_dir)
    lsr = LsrTree(temp_dir, outfmt="list")
    files = lsr.list_files()
    assert any("file1.txt" in f for f in files)
    assert any("file2.txt" in f for f in files)
    assert any("empty_folder/(((empty folder)))" in f for f in files)

def test_list_files_json(temp_dir):
    create_files_structure(temp_dir)
    lsr = LsrTree(temp_dir, outfmt="json")
    result = lsr.list_files()
    assert isinstance(result, str)
    data = pd.read_json(StringIO(result), typ='series')
    assert data[0]['files'] == ['file1.txt']
    assert data[1]['files'] == ['file2.txt']

def test_list_files_string(temp_dir):
    create_files_structure(temp_dir)
    lsr = LsrTree(temp_dir, outfmt="string")
    result = lsr.list_files()
    assert isinstance(result, str)
    assert "file1.txt" in result
    assert "file2.txt" in result

def test_list_files_dataframe(temp_dir):
    create_files_structure(temp_dir)
    lsr = LsrTree(temp_dir, outfmt="dataframe")
    df = lsr.list_files()
    assert isinstance(df, pd.DataFrame)
    assert "file1.txt" in df["file"].values
    assert "file2.txt" in df["file"].values
    assert "Empty Folder" in "".join(df["file"].astype(str).values)

def test_list_files_tree(temp_dir):
    create_files_structure(temp_dir)
    lsr = LsrTree(temp_dir, outfmt="tree", with_counts=True)
    result = lsr.list_files()
    assert hasattr(result, "__iter__")
    result_str = "\n".join(str(r) for r in result)
    assert "file1.txt" in result_str
    assert "file2.txt" in result_str
    assert "Empty Folder" in result_str

def test_nonexistent_path():
    lsr = LsrTree("/nonexistent/path", outfmt="list")
    result = lsr.list_files()
    assert result is None

def test_empty_folder(temp_dir):
    lsr = LsrTree(temp_dir, outfmt="list")
    result = lsr.list_files()
    assert result == []

def test_get_md5(temp_dir):
    file_path = os.path.join(temp_dir, "file.txt")
    with open(file_path, "w") as f:
        f.write("abc")
    md5 = LsrTree.get_md5(file_path)
    expected = hashlib.md5(b"abc").hexdigest()
    assert md5 == expected
