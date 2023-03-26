# PIP INSTALLS
pip install torch
pip install transformers
pip install nltk
pip install textwrap3
pip install git+https://github.com/boudinfl/pke.git
pip install flashtext
pip install sense2vec
pip install sentence_transformers
pip install strsim


# SentencePiece
pip install .\sentencepiece-0.1.97-cp311-cp311-win_amd64.whl

# Download langague model
python -m spacy download en

# Download sense vectors
iwr -outf s2v_reddit_2015_md.tar.gz https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2015_md.tar.gz
tar -xvf  s2v_reddit_2015_md.tar.gz