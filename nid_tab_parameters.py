# Copyright (c) 2026 Ikuo Obataya (obataya@qd-japan.com)
# Licensed under the MIT License
"""
Nanosurf AFMのNIDファイルのヘッダーを解析し、測定パラメーターを抽出してコンマ区切りで出力するスクリプト。
現在のバージョンでは抽出したいパラメータはこのスクリプトにハードコード。

使用例:
    python nid_tab_parameters.py C:/Data
    上記コマンドは、C:/Dataディレクトリ内のすべての.nidファイルのパラメータを抽出し、コンマ区切りで標準出力に表示します。
注意:
"""
import os
import re
import sys
from pathlib import Path

def clean_unicode_artifacts(text):
    """
    Unicode関連のジャンク文字を除去・修正する
    """
    # 一般的なジャンク文字パターンを修正
    replacements = {
        'Â°': '°',  # degree symbol
        'Âµ': 'µ',  # micro symbol 
        'Â': '',    # standalone Â characters
        '\x00': '', # null bytes
        '\ufeff': ''  # BOM
    }
    
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # 追加の制御文字除去
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', cleaned)
    
    return cleaned

def safe_read_file(filepath, max_lines=300):
    """
    複数のエンコーディングを試してファイルを安全に読み取る
    """
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            lines = []
            with open(filepath, 'r', encoding=encoding) as f:
                for i in range(max_lines):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(clean_unicode_artifacts(line))
            return lines
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # 最後の手段：バイナリモードで読んでエラーを無視
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(clean_unicode_artifacts(line))
        return lines
    except Exception as e:
        print(f"Warning: Could not read file {filepath}: {e}")
        return []

def extract_parameters_from_nid(directory: Path):
    """
    NIDファイルのヘッダーを解析し、測定パラメーターを抽出してコンマ区切りで出力する。
    次のようなヘッダのScan, Feedbackのパラメータを列挙する。
    -- Scan --=--------
    Image size=400nm
    Scan direction=Up
    Time/Line=100ms
    Points=512 
    Lines=256 
    X-Slope=-374m°
    Y-Slope=-236m°
    Rotation=0 °
    X-Pos=-1.72µm
    Y-Pos=-3.36µm
    Z-Plane=-3.63nm
    Overscan=10 %
    Line mode=Standard
    Date=14-04-2022
    Time=14:26:35
    -- Feedback --=--------
    Setpoint=85 %
    P-Gain=1000 
    I-Gain=2500 
    D-Gain=0 
    P-Gain2=0 
    I-Gain2=1000 
    D-Gain2=0 
    Tip voltage=0 V
    Feedback mode=Free
    Feedback algo.=Standard PID
    Vibration freq.=178.296kHz
    Vibration ampl.=101mV
    Excitation ampl.=99.2mV
    Ref. phase=0.33k°
    Error range=10 V
    Ampl. Ctrl. mode=Const. Drive
    """
    # パラメーター辞書
    export_lines = []
    params = {
        "Image size": "",
        "Scan direction": "",
        "Time/Line": "",
        "Points": "",
        "Lines": "",
        "X-Slope": "",
        "Y-Slope": "",
        "Rotation": "",
        "X-Pos": "",
        "Y-Pos": "",
        "Z-Plane": "",
        "Overscan": "",
        "Line mode": "",
        "Date": "",
        "Time": "",
        # Feedback
        "Setpoint": "",
        "P-Gain": "",
        "I-Gain": "",
        "D-Gain": "",
        "P-Gain2": "",
        "I-Gain2": "",
        "D-Gain2": "",
        "Tip voltage": "",
        "Feedback mode": "",
        "Feedback algo.": "",
        "Vibration freq.": "",
        "Vibration ampl.": "",
        "Excitation ampl.": "",
        "Ref. phase": "",
        "Error range": "",
        "Ampl. Ctrl. mode": ""
    }
    # ヘッダ行をexport_linesに追加。第一列にはファイル名を入れる。
    header_line = "File Name," + ",".join(params.keys())
    export_lines.append(header_line)

    # NIDファイルを処理
    try:
        for filepath in directory.glob("*.nid"):
            # 安全にファイルを読み取る
            lines = safe_read_file(filepath)
            
            for line in lines:
                if not line: 
                    continue
                for key in params.keys():
                    if key is not None and line.startswith(key + "="):
                        # 値を抽出し、さらにクリーニング
                        value = line.split("=", 1)[1].strip()
                        params[key] = clean_unicode_artifacts(value)
                        break
            
            # コンマ区切りで出力（値もクリーニング）
            cleaned_values = [clean_unicode_artifacts(params[key]) for key in params.keys()]
            output = f"{filepath.name}," + ",".join(cleaned_values)
            export_lines.append(output)

            # params内をフラッシュ
            for key in params.keys():
                params[key] = ""
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")
    
    # 最終的な出力をnid_parameters.csvに保存
    output_file = directory / "nid_parameters.csv"
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            for line in export_lines:
                # 最終出力でもクリーニングを適用
                cleaned_line = clean_unicode_artifacts(line)
                f.write(cleaned_line + "\n")
        print(f"Parameters extracted and saved to {output_file}")
        print(f"Processed {len(export_lines)-1} NID files")  # ヘッダー行を除く
    except Exception as e:
        print(f"Error writing to file {output_file}: {e}")


if __name__ == "__main__":
    # デフォルト設定はカレントディレクトリ。
    target_dir = Path.cwd()
    # 因数があればそれをディレクトリとして使用。
    if len(sys.argv) >= 2:
        target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Error: Directory '{target_dir}' does not exist.")
    else:
        print(f"Processing directory: {target_dir}")
        extract_parameters_from_nid(target_dir)
