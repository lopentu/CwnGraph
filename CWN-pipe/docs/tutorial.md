# CWN Pipeline 教學手冊

本教學將帶你完成一次完整的 Chinese WordNet 資料更新流程。

## 情境說明

假設我們是 CWN 團隊的編輯人員，今天收到以下更新需求：

1. **新增詞目**：「人工智慧」、「機器學習」、「深度學習」
2. **新增義項**：為這些新詞目建立定義與例句
3. **建立語意關係**：標註這些詞彙之間的上下位關係

## 前置準備

### 1. 安裝環境

```bash
# 進入專案目錄
cd /path/to/CWN-pipe

# 建立虛擬環境並安裝
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2. 確認安裝成功

```bash
cwn-update --help
```

---

## Step 1：規劃資料結構

在開始編輯 CSV 之前，我們需要先規劃 ID 編碼：

### ID 編碼規則

| 類型 | 格式 | 範例 |
|------|------|------|
| 詞目 ID (lemma_id) | 6 位數字 | `100001` |
| 義項 ID (sense_id) | 8 位數字 (詞目ID + 2位序號) | `10000101` |
| 義面 ID (facet_id) | 10 位數字 (義項ID + 2位序號) | `1000010101` |

### 本次更新的 ID 規劃

| 詞目 | lemma_id | 義項 sense_id |
|------|----------|---------------|
| 人工智慧 | 100001 | 10000101 |
| 機器學習 | 100002 | 10000201 |
| 深度學習 | 100003 | 10000301 |

---

## Step 2：建立更新資料夾

```bash
# 建立本次更新的資料夾
mkdir -p data/updates/2024-01-ai-terms
cd data/updates/2024-01-ai-terms
```

---

## Step 3：編輯 CSV 檔案

### 3.1 建立 lemmas.csv（詞目）

```csv
lemma_id,lemma,zhuyin,lemma_sno
100001,人工智慧,ㄖㄣˊ ㄍㄨㄥ ㄓˋ ㄏㄨㄟˋ,1
100002,機器學習,ㄐㄧ ㄑㄧˋ ㄒㄩㄝˊ ㄒㄧˊ,1
100003,深度學習,ㄕㄣ ㄉㄨˋ ㄒㄩㄝˊ ㄒㄧˊ,1
```

**欄位說明：**
- `lemma_id`：唯一識別碼，6 位數字
- `lemma`：詞彙本身
- `zhuyin`：注音（字與字之間用空格分隔）
- `lemma_sno`：同形詞序號（通常為 1）

### 3.2 建立 senses.csv（義項）

```csv
sense_id,lemma_id,pos,definition,examples,domain,supplementary
10000101,100001,Na,研究如何使電腦具有人類智慧能力的科學領域，包括學習、推理、問題解決等。,<人工智慧>正在改變我們的生活。|這門課介紹<人工智慧>的基本原理。,資訊科技,又稱 AI
10000102,100001,Na,具有智慧能力的電腦系統或程式。,這個<人工智慧>可以下圍棋。|公司開發了一套客服<人工智慧>。,資訊科技,
10000201,100002,Na,人工智慧的一個分支，研究如何讓電腦從資料中自動學習規律並做出預測。,<機器學習>需要大量的訓練資料。|他正在研究<機器學習>演算法。,資訊科技,
10000301,100003,Na,機器學習的一種方法，使用多層神經網路來學習資料的複雜特徵。,<深度學習>在影像辨識上表現優異。|AlphaGo 使用了<深度學習>技術。,資訊科技,
```

**欄位說明：**
- `sense_id`：義項 ID，8 位數字
- `lemma_id`：所屬詞目 ID
- `pos`：詞性（Na=普通名詞, VH=狀態動詞 等）
- `definition`：定義
- `examples`：例句，多個例句用 `|` 分隔，詞彙用 `<>` 標記
- `domain`：語意領域
- `supplementary`：補充說明

### 3.3 建立 relations.csv（語意關係）

```csv
src_id,tgt_id,edge_type
10000201,10000101,hyponym
10000301,10000201,hyponym
10000101,10000102,nearsynonym
```

**關係說明：**
- `機器學習` 是 `人工智慧` 的**下位詞** (hyponym)
- `深度學習` 是 `機器學習` 的**下位詞** (hyponym)
- `人工智慧(領域)` 與 `人工智慧(系統)` 是**近義詞** (nearsynonym)

**常用關係類型：**

| edge_type | 中文 | 說明 | 範例 |
|-----------|------|------|------|
| hypernym | 上位詞 | A 的上位概念是 B | 狗 → 動物 |
| hyponym | 下位詞 | A 的下位概念是 B | 動物 → 狗 |
| synonym | 同義詞 | A 與 B 同義 | 電腦 ↔ 計算機 |
| nearsynonym | 近義詞 | A 與 B 意思相近 | 高興 ↔ 快樂 |
| antonym | 反義詞 | A 與 B 意思相反 | 大 ↔ 小 |
| holonym | 整體詞 | A 是 B 的整體 | 手 → 身體 |
| meronym | 部分詞 | A 是 B 的部分 | 身體 → 手 |

---

## Step 4：驗證資料

在套用更新前，先驗證資料格式是否正確。

```bash
# 回到專案根目錄
cd /path/to/CWN-pipe

# 執行驗證
cwn-update validate ./data/updates/2024-01-ai-terms/
```

**預期輸出：**

```
╭──────────────╮
│ Load Summary │
╰──────────────╯
┏━━━━━━━━━━━┳━━━━━━━┓
┃ Type      ┃ Count ┃
┡━━━━━━━━━━━╇━━━━━━━┩
│ lemmas    │     3 │
│ senses    │     4 │
│ facets    │     0 │
│ synsets   │     0 │
│ relations │     3 │
└───────────┴───────┘

╭────────────────────╮
│ Validation Results │
╰────────────────────╯
✓ Data is valid
```

### 常見錯誤處理

**錯誤 1：Duplicate ID**
```
Errors (1):
  [unique_id] Duplicate sense_id: 10000101
```
→ 解決：檢查是否有重複的 ID

**錯誤 2：Referential Integrity**
```
Errors (1):
  [referential_integrity] Sense 10000101 references non-existent lemma 999999
```
→ 解決：確認 sense 的 lemma_id 對應到存在的 lemma

**錯誤 3：Missing Node**
```
Errors (1):
  [missing_node] Relation target node not found: 99999999
```
→ 解決：確認 relation 的 src_id 和 tgt_id 都存在

---

## Step 5：套用更新

驗證通過後，產生新的資料檔案。

### 5.1 從頭建立（無基礎資料）

```bash
cwn-update apply ./data/updates/2024-01-ai-terms/ \
    --output ./output/cwn-graph-tutorial.pyobj \
    --version v.tutorial.01
```

### 5.2 增量更新（有基礎資料）

如果你有現有的 CWN 資料：

```bash
cwn-update apply ./data/updates/2024-01-ai-terms/ \
    --base ~/.cwn_graph/cwn-graph-v.2022.05.13.pyobj \
    --output ./output/cwn-graph-updated.pyobj \
    --version v.2024.01.15
```

**輸出：**

```
Loaded 10 records
✓ Validation passed

╭─────────────────╮
│ Export Complete │
╰─────────────────╯
  Version: v.tutorial.01
  Nodes: 7
  Edges: 6
  Output: ./output/cwn-graph-tutorial.pyobj
```

---

## Step 6：檢視結果

### 6.1 查看資料統計

```bash
cwn-update info ./output/cwn-graph-tutorial.pyobj
```

**輸出：**

```
╭────────────────╮
│ CWN Image Info │
╰────────────────╯

Metadata:
  version: v.tutorial.01
  label: cwn-graph-v.tutorial.01
  updated_at: 2024-01-15T10:30:00
  node_count: 7
  edge_count: 6

Nodes:
┏━━━━━━━━┳━━━━━━━┓
┃ Type   ┃ Count ┃
┡━━━━━━━━╇━━━━━━━┩
│ lemma  │     3 │
│ sense  │     4 │
│ Total  │     7 │
└────────┴───────┘

Edges:
┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Type        ┃ Count ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ has_sense   │     4 │
│ hyponym     │     2 │
│ nearsynonym │     1 │
│ Total       │     6 │
└─────────────┴───────┘
```

### 6.2 用 Python 載入驗證

```python
import pickle

# 載入資料
with open("./output/cwn-graph-tutorial.pyobj", "rb") as f:
    V, E, meta = pickle.load(f)

# 查看詞目
for nid, ndata in V.items():
    if ndata.get("node_type") == "lemma":
        print(f"{nid}: {ndata['lemma']}")

# 輸出：
# 100001: 人工智慧
# 100002: 機器學習
# 100003: 深度學習

# 查看義項
for nid, ndata in V.items():
    if ndata.get("node_type") == "sense":
        print(f"{nid}: {ndata['def'][:30]}...")

# 查看關係
for (src, tgt), edata in E.items():
    print(f"{src} --[{edata['edge_type']}]--> {tgt}")
```

---

## Step 7：輸出 Web 格式（選用）

如果需要部署到 CwnWeb：

```bash
cwn-update export-web ./output/cwn-graph-tutorial.pyobj \
    --output ./output/cwn_web/
```

這會產生：
- `word_map.json`：詞彙索引
- `cwn_web_data_0.json` ~ `cwn_web_data_49.json`：分割的資料檔
- `cwn-pos-label.json`：詞性標記說明

---

## 練習題

### 練習 1：新增動詞詞目

新增「訓練」這個詞，包含：
- 詞目：訓練
- 義項 1：(VH) 反覆練習某種技能或行為
- 義項 2：(VC) 讓機器學習模型從資料中學習

### 練習 2：建立語意關係

為「訓練(機器學習)」建立與「機器學習」的關係。

### 練習 3：新增義面

為「人工智慧」的第一個義項新增義面：
- 義面 1：強調理論研究面向
- 義面 2：強調應用開發面向

---

## 附錄：完整 CSV 欄位參考

### lemmas.csv

| 欄位 | 必填 | 格式 | 說明 |
|------|------|------|------|
| lemma_id | ✓ | 6 位數字 | 詞目唯一識別碼 |
| lemma | ✓ | 文字 | 詞彙 |
| zhuyin | | 文字 | 注音（空格分隔） |
| lemma_sno | | 整數 | 同形詞序號，預設 1 |

### senses.csv

| 欄位 | 必填 | 格式 | 說明 |
|------|------|------|------|
| sense_id | ✓ | 8 位數字 | 義項唯一識別碼 |
| lemma_id | ✓ | 6 位數字 | 所屬詞目 ID |
| pos | ✓ | 詞性代碼 | 如 Na, VH, VJ 等 |
| definition | ✓ | 文字 | 定義 |
| examples | | 文字 | 例句，`\|` 分隔，詞彙用 `<>` 標記 |
| domain | | 文字 | 語意領域 |
| supplementary | | 文字 | 補充說明 |

### facets.csv

| 欄位 | 必填 | 格式 | 說明 |
|------|------|------|------|
| facet_id | ✓ | 10 位數字 | 義面唯一識別碼 |
| sense_id | ✓ | 8 位數字 | 所屬義項 ID |
| pos | | 詞性代碼 | 詞性（可選） |
| definition | ✓ | 文字 | 定義 |
| examples | | 文字 | 例句 |

### relations.csv

| 欄位 | 必填 | 格式 | 說明 |
|------|------|------|------|
| src_id | ✓ | 節點 ID | 來源節點 |
| tgt_id | ✓ | 節點 ID | 目標節點 |
| edge_type | ✓ | 關係類型 | 見關係類型表 |

---

## 常見問題

**Q: ID 要怎麼編號？**

A: 建議與團隊協調，取得可用的 ID 範圍。一般來說：
- 新詞目從某個起始數字開始遞增
- 義項 ID = 詞目 ID + 2 位序號（01, 02, 03...）

**Q: 例句中的詞彙一定要用 `<>` 標記嗎？**

A: 是的，這是 CWN 的慣例，用於標示目標詞在例句中的位置。

**Q: 可以刪除現有資料嗎？**

A: 目前 pipeline 主要設計為「新增」和「修改」，刪除功能需謹慎使用。如需刪除，請直接編輯基礎資料。

---

## 下一步

- 閱讀 [CwnGraph 文件](https://cwngraph.readthedocs.io/) 了解如何查詢資料
- 參考 `data/templates/` 中的範本檔案
- 有問題請聯繫 CWN 團隊
