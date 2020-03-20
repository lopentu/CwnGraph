pandoc CwnQuery_doc.ipynb -f ipynb -t rst -s -o temp.rst

echo -e 'API Quick Start\n--------------\n\n' > CwnQuery.rst
cat temp.rst >> CwnQuery.rst
rm temp.rst

