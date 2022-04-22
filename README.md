### PDF2MARC
Automatic cataloging of Theses and Dissertations in RDA MARC21 records.

#### Installation
Download the source code using git or as a zip.
```bash
# Git
git clone https://github.com/lhernandez0/PDF2MARC
# Github client
gh repo clone lhernandez0/PDF2MARC
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
nltk.download('all')
```
Installation notes may be found [in the faq](#installation-notes).

#### Configuration
PDF2MARC uses yaml as config files because they are highly readable and editable with no prior experience. Your project directory should look a little like this:

    .PDF2MARC
    ├───document_patterns
    │   └───document_config.yaml
    ├───entity_patterns
    │   ├───college.yaml
    │   ├───universities.yaml
    │   └───degree_programs.yaml
    ├───static
    │   ├───css
    │   └───js
    └───templates

- **document_config.yaml** Replace this with the City or State of your library as you would have it appear in the Statement of Responsibility.
 ```yaml
 city/state : "Quezon City"
 ```

- **universities.yaml** Contains the list of names your university or university system goes by. These are the patterns in the document that the program will look for.
```yaml
UP DILIMAN : UNIV
University of the Philippines DILIMAN : UNIV
UP Los Baños : UNIV
University of the Philippines Los Baños : UNIV
UP Los Banos : UNIV
University of the Philippines Los Banos : UNIV
```
- **college.yaml** Contains the list of college names and departments of your university. These are the patterns in the document that the program will look for.
```yaml
College of Architecture : COLL
Department of Art Studies : DEPT
College of Arts and Letters : COLL
Department of Art Studies : DEPT
```

TODO: Test behavior for standalone colleges or universities with no constituent colleges.
#### Usage
To run the program on your web-browser for the interactive experience or to fiddle with it before deploying on your webserver:
```bash
python3 app.py
```
And [open localhost on port 4000.](http://127.0.0.1:4000/ "open localhost on port 4000.")

#### Terminal Usage [to do]
PDF2MARC can be used in terminal to quickly create marc records of a file or a directory of files.

Open the program on your terminal using:
```bash
python3 pdf2marc.py [args]
```

### FAQ
#### Why "PDF2MARC"?
PDF2MARC began as an ambitious project for automatic cataloging of any electronic document, especially monographs. Due to practical limitations, I had to limit the prototype to cataloging documents that are diverse enough to be worth automatically cataloging, but structured and predictable enough to design a system for, thus, theses and dissertations.

#### Installation notes
PDF2MARC is *not* a batteries-included solution. It requires a certain level of technical skill and is designed to be operable by a typical systems librarian. It is forkable, or downloadable and modifiable using config files.

PDF2MARC was built using Python 3.9.6 and compatibility has not been tested outside of Windows 10 and Ubuntu 20.04 (LTS) x64.
