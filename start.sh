# conda deactivate
# python3 main.py
if [ "$(which python)" == "/home/eryan/anaconda3/bin/python" ]; then
    # echo "conda activated"
    conda deactivate
fi
python3 main.py
