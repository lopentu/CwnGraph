CwnGraph: Cwn Python API 程式介面
=========


> Chinese Wordnet with Graph Interface

說明文件：[readthedocs](https://cwngraph.readthedocs.io/en/latest/)

CwnGraph 0.3.0 版資料下載：
[Google Drive](https://drive.google.com/file/d/1C_Hg3ZCKjAe6mVbo-EA7a-AZdpjr5wd-/view?usp=sharing)

# QuickStart

## 1. Installation

Start with CwnGraph 0.3.0, there is no additional installation step when using the package. 
You can access the latest data directly with `CwnImage.latest()`, and the package would download the data automatically.
Or, the original version (v0.1.0) is still available with `CwnBase()`

## 2. Load CWN data

To query CWN, the first step is to initialize the cwn data as an object with CwnBase():

```python
from CwnGraph import CwnImage
cwn = CwnImage.latest()
# the original base data
# from CwnGraph import CwnImage
# cwn = CwnBase()
```

Now, you can start querying CWN with the methods provided by CwnImage!

## 3. Basic Query

### 3.1 Query senses from lemmas

To locate a particular sense in CWN, one approach is to first find the lemma associated with that sense. You can use CwnBase.find_lemma() to search for lemmas containing the given RegEx pattern passed as the argument. The example below searches for lemmas containing the string "電腦":

```python
lemmas = cwn.find_lemma("電腦")
lemmas
```

```
[<CwnLemma: 電腦_1>, <CwnLemma: 電腦化_1>, <CwnLemma: 微電腦_1>]
```

This returns a list of matching lemmas (CwnLemma).

Each lemma may itself contain other informations, for example, a lemma (e.g. 電腦_1) may has several senses:

```python
senses = lemmas[0].senses
senses
```

```
[<CwnSense[06613601](電腦): 一種資料處理裝置，能自動接受並儲存、處理輸入的資料，然後經由一組預先存放在機器內的指令逐步引導下產生輸出結果。>,
 <CwnSense[06613602](電腦): 研究或操作電腦的知識。>,
 <CwnSense[06613603](電腦): 比喻計算或記憶能力很強的人。>]
```

## 3.2 Sense

A sense could have several relations with other types of data, e.g. facets of the sense, other senses, etc.

### 3.2.1 Relations

With the relations attribute of a sense, one can find its sense relations to other entities, represented as a list of tuple, with each tuple representing a relation (an edge with the first element as the edgetype, the second as the other node, and the third as the direction).

```python
computer = senses[0]
computer.relations
```

```
[('has_facet', <CwnFacet[0661360101](電腦): 普通名詞。電腦的功能，通常包括程式、軟體等。>, 'forward'),
 ('has_facet',
  <CwnFacet[0661360102](電腦): 普通名詞。電腦的實體，特別指外表，通常包括螢幕、鍵盤、主機等。>,
  'forward'),
 ('is_synset',
  <CwnSynset[syn_004128]: 一種資料處理裝置，能自動接受並儲存、處理輸入的資料，然後經由一組預先存放在機器內的指令逐步引導下產生輸出結果。>,
  'forward'),
 ('hypernym', <CwnSense[06582901](工具): 工作時必須使用的具有特定功能的器具。>, 'forward'),
 ('hyponym', <CwnSense[06582901](工具): 工作時必須使用的具有特定功能的器具。>,
```
