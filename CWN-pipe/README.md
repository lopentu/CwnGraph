# CWN Pipeline

Chinese WordNet (CWN) 資料更新管線工具。

## 安裝

```bash
# 使用 uv 安裝
uv pip install -e .

# 或安裝開發依賴
uv pip install -e ".[dev]"
```

## 快速開始

### 1. 準備 CSV 資料

在更新目錄中準備以下 CSV 檔案：

```
updates/
├── lemmas.csv      # 詞目資料
├── senses.csv      # 義項資料
├── facets.csv      # 義面資料 (選填)
├── synsets.csv     # 同義詞集資料 (選填)
└── relations.csv   # 語意關係資料
```

### 2. 驗證資料

```bash
# 驗證 CSV 資料格式
cwn-update validate ./updates/

# 搭配現有資料檢查參照完整性
cwn-update validate ./updates/ --base cwn-graph-latest.pyobj
```

### 3. 查看差異

```bash
# 比較 CSV 資料與現有資料的差異
cwn-update diff ./updates/ --base cwn-graph-latest.pyobj
```

### 4. 套用更新

```bash
# 從頭建立新的資料集
cwn-update apply ./updates/ --output ./output/cwn-graph-new.pyobj

# 增量更新現有資料
cwn-update apply ./updates/ --base cwn-graph-latest.pyobj --output ./output/cwn-graph-updated.pyobj --version v.2024.01.15
```

### 5. 輸出網頁格式 (CwnWeb)

```bash
# 將 .pyobj 轉換為 CwnWeb 格式
cwn-update export-web cwn-graph-latest.pyobj --output ./cwn_web/
```

### 6. 查看資料資訊

```bash
# 顯示 .pyobj 檔案的統計資訊
cwn-update info cwn-graph-latest.pyobj
```

## CSV 格式說明

### lemmas.csv - 詞目

| 欄位 | 必填 | 說明 |
|------|------|------|
| lemma_id | ✓ | 詞目 ID (6 位數字) |
| lemma | ✓ | 詞彙 |
| zhuyin | | 注音 |
| lemma_sno | | 同形詞序號 (預設 1) |

### senses.csv - 義項

| 欄位 | 必填 | 說明 |
|------|------|------|
| sense_id | ✓ | 義項 ID (8 位數字) |
| lemma_id | ✓ | 所屬詞目 ID |
| pos | ✓ | 詞性標記 |
| definition | ✓ | 定義 |
| examples | | 例句 (以 `\|` 分隔多個例句) |
| domain | | 語意領域 |
| supplementary | | 補充說明 |

### facets.csv - 義面

| 欄位 | 必填 | 說明 |
|------|------|------|
| facet_id | ✓ | 義面 ID (10 位數字) |
| sense_id | ✓ | 所屬義項 ID |
| pos | | 詞性標記 |
| definition | ✓ | 定義 |
| examples | | 例句 |

### synsets.csv - 同義詞集

| 欄位 | 必填 | 說明 |
|------|------|------|
| synset_id | ✓ | 同義詞集 ID (syn_XXXXXX) |
| gloss | ✓ | 同義詞集釋義 |
| pos | | 詞性標記 |
| examples | | 例句 |
| pwn_word | | Princeton WordNet 對應詞 |
| pwn_id | | Princeton WordNet ID |

### relations.csv - 語意關係

| 欄位 | 必填 | 說明 |
|------|------|------|
| src_id | ✓ | 來源節點 ID |
| tgt_id | ✓ | 目標節點 ID |
| edge_type | ✓ | 關係類型 |

**支援的關係類型 (edge_type)：**

| 英文 | 中文 | 說明 |
|------|------|------|
| hypernym | 上位詞 | A 是 B 的上位概念 |
| hyponym | 下位詞 | A 是 B 的下位概念 |
| holonym | 整體詞 | A 是 B 的整體 |
| meronym | 部分詞 | A 是 B 的部分 |
| synonym | 同義詞 | A 與 B 同義 |
| nearsynonym | 近義詞 | A 與 B 近義 |
| antonym | 反義詞 | A 與 B 反義 |
| paranym | 類義詞 | A 與 B 類義 |
| variant | 異體 | A 是 B 的異體 |
| varword | 異體詞 | A 是 B 的異體詞 |
| is_synset | 同義詞集 | A 屬於同義詞集 B |
| has_instance | 事例 | A 有事例 B |
| instance_of | 之事例 | A 是 B 的事例 |

## 程式庫使用

```python
from cwn_pipeline import CsvLoader, CwnValidator, CwnTransformer, CwnExporter

# 載入 CSV 資料
loader = CsvLoader()
data = loader.load_directory("./updates/")

# 驗證資料
validator = CwnValidator()
result = validator.validate(data)
if not result.is_valid:
    print("驗證失敗:", result.errors)

# 轉換為 CwnGraph 格式
transformer = CwnTransformer()
cwn_data = transformer.transform(data, version="v.2024.01.15")

# 輸出
exporter = CwnExporter("./output/")
exporter.export_pyobj(cwn_data)
```

## 專案結構

```
cwn-pipeline/
├── src/cwn_pipeline/
│   ├── __init__.py
│   ├── cli.py              # CLI 命令
│   ├── schemas/            # 資料格式定義
│   │   ├── enums.py        # 列舉類型
│   │   ├── nodes.py        # 節點 schema
│   │   └── relations.py    # 關係 schema
│   └── pipeline/           # 處理管線
│       ├── loader.py       # CSV 載入
│       ├── validator.py    # 資料驗證
│       ├── differ.py       # 差異計算
│       ├── transformer.py  # 資料轉換
│       └── exporter.py     # 輸出匯出
├── data/
│   └── templates/          # CSV 範本
├── tests/                  # 測試
├── pyproject.toml
└── README.md
```

## 授權

GPL-3.0
