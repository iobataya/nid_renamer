# nid_renamer and nid_tab_parameters
## nid_renamer
指定したディレクトリ内のすべてのNanosurfのAFMデータからスキャンパラメーターを読み込み、ファイル名の接頭語に反映させるPythonスクリプトです。

Extract scan parameters from NID files and rename the files to include the parameters

### Usage
```bash
python nid_renamer.py -DTSLXYZAU <path_to_directory>
```

#### Options
```python
D: Date, 日付
T: Time, スキャン開始時刻
S: Image size, イメージサイズ
L: Time/Line, ライン当たりの時間
X: Points, fast軸のピクセル数
Y: Lines, slow軸のライン数
Z: {Points}x{Lines}形式
A: All - すべての情報を接頭語として付加 (DTSLXYZ)
U: Undo - 元の名前がデフォルトのファイル名であれば、すべて元の名前に戻す。(例: Image00001.nid)
```
### Example
```bash
python nid_renamer.py -A data_directory
```
This command will rename all NID files in the specified directory to include the scan parameters in the format of

```20260427_123456_10um_1s_128x128_scan.nid```

## nid_tab_parameters
NanosurfのAFMデータからスキャンパラメーターを抽出し、コンマ区切りのテキストファイルに保存するPythonスクリプトです。列には、ファイル名、イメージサイズ、スキャン方向、ライン当たりの時間などのすべてのスキャンパラメーターとzフィードバック設定が含まれます。

Extract scan parameters from NID file and save to a csv-delimited text file
### Usage
```bash
python nid_tab_parameters.py <path_to_directory>
```
### Example
```bash
python nid_tab_parameters.py data_directory
```
This command will extract scan parameters from all NID files in the specified directory and save them to a file named ``nid_parameters.csv`` in the same directory. The output file will contain the following columns:
- File Name
- Image size
- Direction
- Time/Line
  and all other scan parameters and z-feedback settings.

## Requirements
- Python 3.x
- Nanosurf Image Data (NID) file format

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
