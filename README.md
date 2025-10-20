
1. Create & activate venv
   python -m venv venv
   .\venv\Scripts\activate


2. pip install -r requirements.txt
3. python crawler/generate_synthetic_data.py --rows 5000
4.python etl/clean_data.py
5.python eda/analysis.py
6.Charts will be created in eda/plots/.
