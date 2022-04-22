###PDF2MARC
Automatic cataloging of Theses and Dissertations in RDA MARC21 records.

####Installation
Download the source code using git or as a zip.
```bash
# Git
git clone https://github.com/<YOUR-USERNAME>/PDF2MARC
# Github client
gh repo clone <YOUR-USERNAME>/PDF2MARC
```
Move to do the directory and install requirements using pip.
```bash
cd PDF2MARC
pip install -r requirements.txt
```
Additionally, you may need to install NLTK corpora.
Using the terminal
```bash
python3 -m nltk.downloader all
```
Or using the python interpreter
```python
import nltk
nltk.download('punkt')
```

###FAQ
####Why "PDF2MARC"?
PDF2MARC began as an ambitious project for automatic cataloging of any electronic document, especially monographs. Due to practical limitations, I had to limit the prototype to cataloging documents that are diverse enough to be worth automatically cataloging, but structured and predictable enough to design a system for, thus, theses and dissertations.

####Installation notes
PDF2MARC is *not* a batteries-included solution. It requires a certain level of technical skill and is designed to be operable by a typical systems librarian. It is forkable, or downloadable and modifiable using config files.

PDF2MARC was built using Python 3.9.6 and compatibility has not been tested outside of Windows 10 and Ubuntu 20.04 (LTS) x64.
