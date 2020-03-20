API Quick Start
----------------


.. container:: cell markdown

   This is a quick guide to using ``CwnGraph`` API to query and navigate
   `Chinese Wordnet <http://lope.linguistics.ntu.edu.tw/cwn2/>`__.

.. container:: cell markdown

   .. rubric:: 1. Installation
      :name: 1-installation

   When using ``CwnGraph`` for the **first time**, you would need to
   download and install the data for cwn (``cwn_graph.pyobj``) with
   ``CwnBase.install_cwn()``:

.. container:: cell code

   .. code:: python

      from pprint import pprint
      from CwnGraph import CwnBase
      CwnBase.install_cwn("data/cwn_graph.pyobj")

   .. container:: output stream stdout

      ::

         CWN data installed

.. container:: cell markdown

   .. rubric:: 2. Load CWN data
      :name: 2-load-cwn-data

   To query CWN, the first step is to initialize the cwn data as an
   object with ``CwnBase()``:

.. container:: cell code

   .. code:: python

      from CwnGraph import CwnBase
      cwn = CwnBase()

.. container:: cell markdown

   Now, you can start querying CWN with the methods provided by
   ``CwnBase``!

.. container:: cell markdown

   .. rubric:: 3. Basic Query
      :name: 3-basic-query

.. container:: cell markdown

   .. rubric:: 3.1 Query senses from lemmas
      :name: 31-query-senses-from-lemmas

   To locate a particular sense in CWN, one approach is to first find
   the lemma associated with that sense. You can use
   ``CwnBase.find_lemma()`` to search for lemmas containing the given
   RegEx pattern passed as the argument. The example below searches for
   lemmas containing the string ``"電腦"``:

.. container:: cell code

   .. code:: python

      lemmas = cwn.find_lemma("電腦")
      lemmas

   .. container:: output execute_result

      ::

         [<CwnLemma: 電腦_1>, <CwnLemma: 電腦化_1>, <CwnLemma: 微電腦_1>]

.. container:: cell markdown

   This returns a list of matching lemmas (``CwnLemma``).

   Each lemma may itself contain other informations, for example, a
   lemma (e.g. ``電腦_1``) may has several senses:

.. container:: cell code

   .. code:: python

      senses = lemmas[0].senses
      senses

   .. container:: output execute_result

      ::

         [<CwnSense[06613601](電腦): 一種資料處理裝置，能自動接受並儲存、處理輸入的資料，然後經由一組預先存放在機器內的指令逐步引導下產生輸出結果。>,
          <CwnSense[06613602](電腦): 研究或操作電腦的知識。>,
          <CwnSense[06613603](電腦): 比喻計算或記憶能力很強的人。>]

.. container:: cell markdown

   .. rubric:: 3.2 Sense
      :name: 32-sense

   A sense could have several relations with other types of data, e.g.
   facets of the sense, other senses, etc.

   .. rubric:: 3.2.1 Relations
      :name: 321-relations

   With the ``relations`` attribute of a sense, one can find its **sense
   relations** to other entities, represented as a list of tuple, with
   each tuple representing a relation (an edge with the first element as
   the *edgetype*, the second as *the other node*, and the third as the
   *direction*).

.. container:: cell code

   .. code:: python

      computer = senses[0]
      computer.relations

   .. container:: output execute_result

      ::

         [('has_facet', <CwnFacet[0661360101](電腦): 普通名詞。電腦的功能，通常包括程式、軟體等。>, 'forward'),
          ('has_facet',
           <CwnFacet[0661360102](電腦): 普通名詞。電腦的實體，特別指外表，通常包括螢幕、鍵盤、主機等。>,
           'forward'),
          ('is_synset',
           <CwnSynset[syn_004128]: 一種資料處理裝置，能自動接受並儲存、處理輸入的資料，然後經由一組預先存放在機器內的指令逐步引導下產生輸出結果。>,
           'forward'),
          ('hypernym', <CwnSense[06582901](工具): 工作時必須使用的具有特定功能的器具。>, 'forward'),
          ('hyponym', <CwnSense[06582901](工具): 工作時必須使用的具有特定功能的器具。>, 'reversed')]

.. container:: cell markdown

   .. rubric:: 3.2.2 Facets
      :name: 322-facets

   Sometimes, a sense may have multiple facets with slightly different
   meanings:

.. container:: cell code

   .. code:: python

      computer.facets

   .. container:: output execute_result

      ::

         [<CwnFacet[0661360101](電腦): 普通名詞。電腦的功能，通常包括程式、軟體等。>,
          <CwnFacet[0661360102](電腦): 普通名詞。電腦的實體，特別指外表，通常包括螢幕、鍵盤、主機等。>]

.. container:: cell markdown

   while other senses may not have facets:

.. container:: cell code

   .. code:: python

      senses[1]

   .. container:: output execute_result

      ::

         <CwnSense[06613602](電腦): 研究或操作電腦的知識。>

.. container:: cell code

   .. code:: python

      # This sense has no facets
      senses[1].facets

   .. container:: output execute_result

      ::

         []

.. container:: cell markdown

   .. rubric:: 3.2.3 Example sentences
      :name: 323-example-sentences

   The example sentences of **a sense** can be retrieved with the
   ``examples`` attribute:

.. container:: cell code

   .. code:: python

      senses[1]

   .. container:: output execute_result

      ::

         <CwnSense[06613602](電腦): 研究或操作電腦的知識。>

.. container:: cell code

   .. code:: python

      senses[1].examples

   .. container:: output execute_result

      ::

         ['小朋友都覺得放假好煩，比上學更累，他們要學<電腦>，上補習班。',
          '這樣規定豈不是加重學生的負擔？還不如學<電腦>或英文更有實效。',
          '陶公我在高一時就認為他<電腦>超強的，但是現在我認為muscle你也不差。']

.. container:: cell markdown

   When a sense has facets, one need to **first retrieve a particular
   facet** to get the examples of this sense facet:

.. container:: cell code

   .. code:: python

      computer.facets[0]

   .. container:: output execute_result

      ::

         <CwnFacet[0661360101](電腦): 普通名詞。電腦的功能，通常包括程式、軟體等。>

.. container:: cell code

   .. code:: python

      computer.facets[0].examples

   .. container:: output execute_result

      ::

         ['走遍大街小巷，如何選一台適合自己的個人<電腦>是一大問題。',
          '健保局總局與六個分局的<電腦>軟硬體與通信費用應限定在十億以內。',
          '一種以藝術大師命名的<電腦>病毒，每年固定在大師誕辰三月六日發作，摧毀被感染<電腦>的所有硬碟檔案。']

.. container:: cell markdown

   However, it may be tedious to check whether a sense has facets before
   retrieving the examples. One could use ``CwnSense.all_examples()`` to
   retrieve **all examples of a sense** whether or not this sense has
   facets:

.. container:: cell code

   .. code:: python

      # Can't retrieve examples for this sense 
      # because they are stored under facets
      computer.examples

   .. container:: output execute_result

      ::

         ''

.. container:: cell code

   .. code:: python

      # This find all examples of a sense 
      # regardless of where the examples are stored
      computer.all_examples()

   .. container:: output execute_result

      ::

         ['走遍大街小巷，如何選一台適合自己的個人<電腦>是一大問題。',
          '健保局總局與六個分局的<電腦>軟硬體與通信費用應限定在十億以內。',
          '一種以藝術大師命名的<電腦>病毒，每年固定在大師誕辰三月六日發作，摧毀被感染<電腦>的所有硬碟檔案。',
          '大家會在這兩天把<電腦>搬進宿舍嗎？',
          '你買這麼漂亮的新<電腦>，發財了喔？',
          '因為<電腦>可以吸磁鐵，所以我就貼了很多磁鐵，但是有人說貼磁鐵的話會影響到主機，這是真的嗎？']

.. container:: cell markdown

   .. rubric:: 3.2.4 Other data of a sense
      :name: 324-other-data-of-a-sense

   Other data of a sense could be retrieved with the ``data()`` method:

.. container:: cell code

   .. code:: python

      senses[1].data()

   .. container:: output execute_result

      ::

         {'annot': {},
          'def': '研究或操作電腦的知識。',
          'domain': '',
          'examples': ['小朋友都覺得放假好煩，比上學更累，他們要學<電腦>，上補習班。',
           '這樣規定豈不是加重學生的負擔？還不如學<電腦>或英文更有實效。',
           '陶公我在高一時就認為他<電腦>超強的，但是現在我認為muscle你也不差。'],
          'node_type': 'sense',
          'pos': 'Na'}

.. container:: cell markdown

   .. rubric:: 3.3 Other approaches to query senses
      :name: 33-other-approaches-to-query-senses

   ``CwnBase`` provides ways to search for senses **directly** with
   ``CwnBase.find_senses()``. This method searches for senses with
   lemmas, sense definitions, or example sentences that match the given
   RegEx patterns. The matched senses are returned as a list of senses.

.. container:: cell code

   .. code:: python

      cwn.find_senses(lemma="^車$")

   .. container:: output execute_result

      ::

         [<CwnSense[06665201](車): 在陸地上以輪子行駛的運輸工具。>,
          <CwnSense[06665202](車): 以車子為形象製成的人造物。>,
          <CwnSense[06665203](車): 開放式用於乘載或放置物品的有輪子的工具。>,
          <CwnSense[06665204](車): 相互連結用在軌道上行駛的運輸工具中的一節。>,
          <CwnSense[06665205](車): 計算一車承載物的量的單位。>,
          <CwnSense[06665206](車): 利用機械切削特定物品。>,
          <CwnSense[06665207](車): 大型的紡織機械。>,
          <CwnSense[06665208](車): 利用機器來縫製衣物。>,
          <CwnSense[07021501](車): 姓。>,
          <CwnSense[07021601](車): 象棋遊戲中所使用的棋子之一，走直線。>]

.. container:: cell code

   .. code:: python

      cwn.find_senses(definition="輪子")

   .. container:: output execute_result

      ::

         [<CwnSense[03027001](輛): 計算有輪子的機械裝置的單位。>,
          <CwnSense[04082906](台): 計算有輪子的機械裝置的單位。>,
          <CwnSense[04153906](臺): 計算有輪子的機械裝置的單位。>,
          <CwnSense[05075709](部): 計算有輪子的機械裝置的單位。>,
          <CwnSense[05131903](輪): 計算輪子的單位。>,
          <CwnSense[05131904](輪): 形狀像輪子的物體。>,
          <CwnSense[06521401](車子): 在陸地上以輪子行駛的運輸工具。>,
          <CwnSense[06552201](汽車): 在陸地上行駛的有四個以上的輪子的運輸工具。>,
          <CwnSense[06665201](車): 在陸地上以輪子行駛的運輸工具。>,
          <CwnSense[06665203](車): 開放式用於乘載或放置物品的有輪子的工具。>,
          <CwnSense[08008101](胎): 輪子外面包覆的環形橡膠製品。為英語tire的音譯。>,
          <CwnSense[09004101](汽): 在陸地上行駛的有四個以上的輪子的運輸工具。>]

.. container:: cell code

   .. code:: python

      cwn.find_senses(examples="學步車")

   .. container:: output execute_result

      ::

         [<CwnSense[05041401](連): 兩物體在空間上相連。>,
          <CwnSense[06665203](車): 開放式用於乘載或放置物品的有輪子的工具。>]
