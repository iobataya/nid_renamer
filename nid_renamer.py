# Copyright (c) 2026 Ikuo Obataya (obataya@qd-japan.com)
# Licensed under the MIT License
"""
Nanosurf AFMのNIDファイルのヘッダーを解析し、オプションに基づいてファイル名をリネームするスクリプト。

オプション:
    D: Date, 日付
    T: Time, スキャン開始時刻
    S: Image size, イメージサイズ
    L: TIme/Line, ライン当たりの時間
    X: Points, fast軸のピクセル数
    Y: Lines, slow軸のライン数
    Z: {Points}x{Lines}形式
    A: すべての情報を接頭語として付加 (DTSLXY)
    U: デフォルトの名前の場合は元の名前に戻す。(Image0010.nidなど)
使用例:
    python nid_renamer.py -DTSZ C:/Data
    上記コマンドは、C:/Dataディレクトリ内のすべての.nidファイルを対象に、日付、時刻、イメージサイズ、Time/Line、解像度をファイル名の接頭語として付加します。
注意:
    - すでに同じ接頭語が付いているファイルはスキップされます。
    - ヘッダーの情報が見つからない場合、その項目はスキップされます。
    - ファイル名の接頭語は、指定されたオプションの順序でアンダースコア "_" で区切られます。
"""
import os
import re
import sys
from pathlib import Path

def clean_text_for_filename(text):
    """
    ファイル名に使用するテキストからジャンク文字を除去し、安全な文字に置換する
    """
    if not text:
        return text
    
    # latin-1で読み取った際に発生する一般的なジャンク文字を修正
    replacements = {
        'Â°': '',    # degree symbol (remove for filename safety)
        'Âµ': 'u',   # micro symbol -> u (µm -> um)
        'Â': '',     # standalone Â characters
        ':': '',     # colon (時刻区切り文字)
        ' ': '',     # spaces
    }
    
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # 追加の制御文字除去
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)
    
    return cleaned

def rename_nid_files(directory: Path, options="DT"):
    """
    NIDファイルのヘッダーを解析し、オプションに基づいてファイル名をリネームする。
    """
    # 正規表現のコンパイル
    re_D = re.compile(r'Date=(\d{2})-(\d{2})-(\d{4})')
    re_T = re.compile(r'Time=(\d{2}):(\d{2}):(\d{2})')
    # Image sizeは数値部分のみをキャプチャし、単位(µm等)は文字化け回避のため個別に処理する
    re_S = re.compile(r'Image size=([\d\.]+)(\w*)')
    re_L = re.compile(r'Time/Line=([\d\.]+\w*)')
    re_X = re.compile(r'Points=(\d+)')
    re_Y = re.compile(r'Lines=(\d+)')
    # もとにもどすオプションのための正規表現。行末がImage0010.nidのように、Image+数字+.nidで終わるものをキャプチャする。接頭語はどんな文字も許容する。
    re_Undo = re.compile(r'^(?:.*_)?(Image\d+\.nid)$')

    # 処理対象のファイル一覧を取得
    target_files = list(directory.glob("*.nid"))
    if not target_files:
        print(f"No .nid files found in: {directory}")
        return

    if "A" in options:
        # Aオプションはすべての情報を付加するため、オプション文字列を上書きして順序を固定する
        options = "DTSLZ"
    for filepath in target_files:
        if not filepath.is_file():
            continue

        filename = filepath.name
        info = {"D": "", "T": "", "S": "", "L": "", "X": "", "Y": ""}
        
        try:
            # latin-1で開くことで、バイナリ混じりのヘッダーでもエラーを避けつつµ等を読み込める
            with open(filepath, 'r', encoding='latin-1') as f:
                for _ in range(300):
                    line = f.readline()
                    if not line: break

                    # Uオプション: デフォルトの名前に戻す
                    if "U" in options:
                        m = re_Undo.search(filename)
                        if m:
                            # ファイルをクローズしないとリネームできない。
                            f.close()
                            new_filename = m.group(1)
                            new_filepath = filepath.with_name(new_filename)
                            os.rename(filepath, new_filepath)
                            print(f"Reverted: {filename} -> {new_filename}")
                            break  # 次のファイルへ

                    # 日付 (DD-MM-YYYY -> YYYYMMDD)
                    if not info["D"]:
                        m = re_D.search(line)
                        if m: info["D"] = clean_text_for_filename(f"{m.group(3)}{m.group(2)}{m.group(1)}")
                    
                    # 時刻 (HH:MM:SS -> HHMMSS)
                    if not info["T"]:
                        m = re_T.search(line)
                        if m: info["T"] = clean_text_for_filename(f"{m.group(1)}{m.group(2)}{m.group(3)}")
                    
                    # サイズ (ジャンク文字を除去してファイル名に安全な形式に)
                    if not info["S"]:
                        m = re_S.search(line)
                        if m: info["S"] = clean_text_for_filename(f"{m.group(1).strip()}{m.group(2).strip()}")
                    
                    # Time/Line
                    if not info["L"]:
                        m = re_L.search(line)
                        if m: info["L"] = clean_text_for_filename(m.group(1).strip())
                    
                    # 解像度
                    if not info["X"]:
                        m = re_X.search(line)
                        if m: info["X"] = clean_text_for_filename(m.group(1))
                    if not info["Y"]:
                        m = re_Y.search(line)
                        if m: info["Y"] = clean_text_for_filename(m.group(1))

            # --- 接頭語の組み立て ---
            parts = []
            if "D" in options and info["D"]: parts.append(info["D"])
            if "T" in options and info["T"]: parts.append(info["T"])
            if "S" in options and info["S"]: parts.append(info["S"])
            if "L" in options and info["L"]: parts.append(info["L"])
            
            # Zオプションは {Points}x{Lines} 形式
            if "Z" in options and info["X"] and info["Y"]:
                parts.append(f"{info['X']}x{info['Y']}")
            else:
                if "X" in options and info["X"]: parts.append(info["X"])
                if "Y" in options and info["Y"]: parts.append(info["Y"])

            if "U" in options and not parts:
                # Uオプションでリネームを元に戻す場合、接頭語がないのが正常なのでスキップ
                continue

            if not parts:
                print(f"Skip: {filename} (Required info not found in header)")
                continue

            # 区切り文字 "_" で結合
            prefix = "_".join(parts) + "_"
            
            # すでにリネーム済みかチェック（二重付加を防止）
            if filename.startswith(prefix):
                print(f"Skip: {filename} (Already has the prefix)")
                continue

            new_filename = prefix + filename
            new_filepath = filepath.with_name(new_filename)

            # Windowsのファイルシステム競合を避けるためos.renameを使用
            os.rename(filepath, new_filepath)
            print(f"Done: {filename} -> {new_filename}")
            print(f"  Extracted info: {info}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # デフォルト設定
    target_dir = Path.cwd()
    cmd_options = "DT"

    # 引数の解析
    # python script.py -DTSZ C:/Data
    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            cmd_options = arg[1:].upper()
        else:
            target_dir = Path(arg)

    if not target_dir.exists():
        print(f"Error: Directory '{target_dir}' does not exist.")
    else:
        print(f"Processing directory: {target_dir}")
        print(f"Options enabled: {cmd_options}")
        rename_nid_files(target_dir, cmd_options)