import spacy
from spacy.matcher import Matcher
import re
import os
import yaml
import fitz
import truecase
from pymarc import Record, Field

def clean_pdf_text(file, document_patterns):
    start_words = document_patterns['abstract_start_words']
    stop_words = document_patterns['abstract_stop_words']
    shortest_abstract = str()
    first_page_as_list = list()
    with fitz.open(file) as doc:
        pdf_text = str()
        start_line = None
        end_line = None
        for index, page in enumerate(doc):
            abstract_list = list()
            text = page.get_text() # https://github.com/pymupdf/PyMuPDF/issues/363, coverting tabs into multiple spaces
            # print(text)
            text = text.split("\n")
            if(index==0):
                first_page_as_list = text
            # https://stackoverflow.com/a/58974732
            # To get the expected output, you need to iterate over a shallow copy of the list, while still removing items from the original list, as follows
            for line in text[:]:
                ignore_line = False
                # remove lines with only roman numerals
                roman_pattern = r"\b(?=[MDCLXVIΙ])M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})([IΙ]X|[IΙ]V|V?[IΙ]{0,3})\b\.?[\s]*$"
                match = re.match(roman_pattern, line, flags=re.DOTALL | re.IGNORECASE)
                line_clean = line.strip().lstrip().lower()
                # print(line)
                if(match):
                    # print("removing:",line)
                    ignore_line = True
                    text.remove(line)
                # Stop checking if end_line is True
                if(end_line is None):
                    if(line_clean in start_words):
                        start_line = line
                        # print(start_line)
                        # empty the shortest_abstract if found a new start_line somehow
                        shortest_abstract = str()
                    else:
                        if(line_clean in stop_words and start_line):
                            end_line = line
                            # print(end_line)
                        else:
                            if(len(line)==1 and abstract_list):
                                # print(f"1 char line '{line}'")
                                abstract_list.append('\n\t')
                            if(line):
                                if(ignore_line == False):
                                    abstract_list.append(line.strip())
            pdf_text += '\n'.join(text)
            # abstract_list.append('\n')
            shortest_abstract += ' '.join(abstract_list)
        shortest_abstract = re.sub('\n[\s]+', '\n\t', shortest_abstract)
        # pdf_text = re.sub(r'\n[\s]+', '\n', pdf_text)
        # print(pdf_text)
        return pdf_text, shortest_abstract, first_page_as_list

def spacy_model(model_name):
    if (model_name == "small"):
        return spacy.load("en_core_web_sm")
    elif (model_name == "medium"):
        return spacy.load("en_core_web_md")
    elif (model_name == "stanford"):
        import spacy_stanza
        return spacy_stanza.load_pipeline("en")
    else:
        print(f"Unknown model: {model_name}")
        exit()

def load_entity_patterns():
    patterns_dict = dict()
    entity_patterns_path = os.path.join(os.getcwd(),'entity_patterns')
    for file in os.listdir(entity_patterns_path):
        file = os.path.join('.\entity_patterns',file)
        if file.endswith('.yaml'):
            with open(file, "r", encoding="utf-8") as f:
                try:
                    file_dict = yaml.safe_load(f)
                    patterns_dict.update(file_dict)
                    print(f"{file} loaded")
                except yaml.YAMLError as exc:
                    print(f"{file} failed to load")
    # print(patterns_dict)
    patterns = []
    for key in patterns_dict:
        # print(f"{patterns_dict[key]} - {key}")
        pattern_item = dict()
        pattern_item["label"] = str(patterns_dict[key]).strip()
        pattern_item["pattern"] = str(key).strip()
        patterns.append(pattern_item)
    return patterns

def load_document_pattern():
    document_dict = dict()
    file = os.path.join(os.getcwd(),'document_patterns', 'document_config.yaml')
    with open(file, "r", encoding="utf-8") as f:
        try:
            document_dict = yaml.safe_load(f)
            print(f"{file} loaded")
        except yaml.YAMLError as exc:
            print(f"{file} failed to load")
    return document_dict

def count_non_filing_characters(title_string):
    non_filing_characters = 0
    non_filing_words = ["a", "the", "an", "L'"]
    for word in non_filing_words:
        pattern = re.compile(r'[^0-9a-zA-Z]*'+word+r'?[^0-9a-zA-Z]*',flags=re.IGNORECASE)
        match = pattern.match(title_string)
        if(match):
            # print(f"Found {match[0]}")
            non_filing_characters = len(match[0])
            title_string = title_string[non_filing_characters:]
            break
    # print(title_string)

    # print("Non-filing characters:",non_filing_characters)
    if(non_filing_characters>9):
        non_filing_characters = 9
    return(non_filing_characters)

def title_case(title):
    exceptions = ["and", "as", "but", "for", "if", "nor", "or", "so", "yet", "a", "an", "the", "as", "at", "by", "for", "in", "of", "off", "on", "per", "to", "up", "via"]
    return ' '.join(x.title() if nm==0 or not x in exceptions else x for nm,x in enumerate(title.split(' ')))

def marc_maker(important_ents, title_string, shortest_abstract, file_path, document_patterns):
    record = Record()
    author_name = "n/a"
    adviser_name = "n/a"
    co_adviser_name = "n/a"
    publishing_date = "n/a"
    publishing_year = "0000"
    college_name = "n/a"
    university_name = "n/a"
    degree_program = "n/a"

    marc_file_path = os.path.splitext(file_path)[0]+'.mrc'

    # Named entities
    for ent in important_ents:
        if (author_name == "n/a"):
            if (ent.label_ == 'PERSON'):
                try:
                    author_name = ent.text.strip()
                    author_name_inverted = author_name.split(" ")
                    author_name_inverted = f"{author_name_inverted[-1]}, {' '.join(author_name_inverted[:-1])}"
                except:
                    print(f"Failed parsing {ent.label_} as author")
                    # Leaving as TODO in case we find an edge case like 1 name author
        if (publishing_date == "n/a"):
            if (ent.label_ == 'DATE'):
                date_pattern = re.compile("[1-3][0-9]{3}")
                date_match = date_pattern.search(ent.text.strip())
                if(date_match):
                    # print(f"Date in {ent.text.strip()}")
                    # print(f"Match is {date_match[0]}")
                    publishing_date = ent.text
                    publishing_year = date_match[0]
                else:
                    # print(f"No date in {ent.text.strip()}")
                    pass
        # Can have a college OR a department, not both
        if (college_name == "n/a"):
            if (ent.label_ == 'COLL' or ent.label_ == 'DEPT'):
                college_name = ent.text.strip() # College and Department will be considered interchangeable in the context of UP Diliman

        if (university_name == "n/a"):
            if (ent.label_ == 'UNIV'):
                university_name = ent.text.strip()

        # Degree program
        if (degree_program == "n/a"):
            if (ent.label_ == 'UNDR' or ent.label_ == 'GRAD' or ent.label_ == 'POST'):
                degree_program = ent.text.strip()
    # 100 Main entry

    record.add_field(Field(
                        tag = '100',
                        indicators = ['1','#'],
                        subfields = ['a', author_name_inverted, 'e', 'author.']
                    ))

    # 245 statement_of_responsibility
    statement_of_responsibility = author_name
    if(adviser_name != "n/a"):
        statement_of_responsibility += f" ; {adviser_name}, adviser"
    statement_of_responsibility += "."
    title_string = truecase.get_true_case(title_string)
    statement_of_responsibility = title_case(statement_of_responsibility)
    record.add_field(Field(
                        tag = '245',
                        indicators = ['1',count_non_filing_characters(title_string)],
                        subfields = ['a', title_string, 'c', statement_of_responsibility]
                    ))


    # Producer statement
    # print("university:", university_name)
    producer_statement = f'{document_patterns["city/state"]} : ' # As defined in document config for now (?)
    if(college_name == "n/a" and university_name == "n/a"):
        print("No university and college found")
        producer_statement = "[Place of publication not identified] :"
    else:
        if(college_name != "n/a"):
            producer_statement += college_name +", "
        if(university_name != "n/a"):
            producer_statement += university_name # Add a comma after?
        producer_statement = title_case(producer_statement)
    record.add_field(Field(
                        tag = '264',
                        indicators = ['#','1'],
                        subfields = ['a', producer_statement, 'c', f"{publishing_year}."]
                    ))

    # Fields 336 to 338 are hardcoded
    record.add_field(Field(
                        tag = '336',
                        indicators = ['#','#'],
                        subfields = ['a', 'text', 'c', 'rdacontent']
                    ))

    record.add_field(Field(
                        tag = '337',
                        indicators = ['#','#'],
                        subfields = ['a', 'unmediated', 'c', 'rdamedia']
                    ))
    record.add_field(Field(
                        tag = '338',
                        indicators = ['#','#'],
                        subfields = ['a', 'volume', 'c', 'rdacarrier']
                    ))

    # 502 - Dissertation Note
    # print("university:", university_name)
    thesis_statement = f"Thesis ({degree_program})--{university_name},"
    record.add_field(Field(
                        tag = '502',
                        indicators = ['#','#'],
                        subfields = ['a', thesis_statement, 'd', f"{publishing_year}."] # d should only contain year, but library seems to be using 'Month Year'
                    ))

    # 520 - Summary, Etc
    record.add_field(Field(
                        tag = '520',
                        indicators = ['3','#'],
                        subfields = ['a', shortest_abstract]
                    ))

    if(adviser_name != "n/a"):
        record.add_field(Field(
                            tag = '700',
                            indicators = ['#','#'],
                            subfields = ['a', adviser_name, 'e', 'adviser.']
                        ))

    record.add_field(Field(
                        tag = '842',
                        indicators = ['#','#'],
                        subfields = ['a', 'Thesis']
                    ))

    # print(record)
    with open(marc_file_path, 'wb') as f:
        try:
            f.write(record.as_marc())
        except:
            try:
                record.force_utf8 = True
                f.write(record.as_marc())
            except:
                print(f"Failed to write {marc_file_path}")
                pass
    return(marc_file_path)
entity_patterns = load_entity_patterns()
document_patterns = load_document_pattern()
# print(patterns)
# Read file
# entity ruler for entity rules
nlp = spacy_model("medium")
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"phrase_matcher_attr": "LOWER"})
ruler.add_patterns(entity_patterns)

def pdf2marc(file_path):
    doc_path = file_path
    pdf_text, shortest_abstract, first_page_as_list = clean_pdf_text(doc_path, document_patterns)
    # pdf_text = re.sub(r'\n+', ' ', pdf_text)
    # do nlp
    doc = nlp(pdf_text)

    important_ents = list()
    for ent in doc.ents:
        important_labels = ["DATE", "GPE", "UNDR", "GRAD", "DPLM", "DEPT", "COLL", "UNIV", "PERSON"]
        if(ent.label_ in important_labels):
            # print(truecase.get_true_case(ent.text.strip()), ent.label_)
            important_ents.append(ent)

    # do nlp to search for title
    # look for the first and all consecutive lines whose entire line is not a named entity
    title_list = list()
    title_string = None
    for line in first_page_as_list:
        if(line.strip()):
            line_nlp = nlp(line)
            ent_list = list()
            for ent in line_nlp.ents:
                # if(ent.label_ in important_labels):
                ent_list.append(ent.text)
                # print(ent.label_,ent.text)
            ent_string = ' '.join(ent_list)
            # print(ent_string.strip(),line.strip())
            if(ent_string.strip()!=line.strip()):
                # the line is not a named entity (University name, author name, etc), and is likely a title text
                title_list.append(line.strip())
            else:
                if(title_list):
                    # title list is partially found, and the new line is likely no longer part of the title
                    title_string = ' '.join(title_list)
                    for stop_word in document_patterns['title_stop_words']:
                        if(stop_word.lower() in title_string.lower()):
                            # print(f"stop_word '{stop_word}' in '{title_string}'")
                            stop_word_in_line = re.search(stop_word, title_string, flags=re.IGNORECASE)[0]
                            # print(stop_word_in_line)
                            if(stop_word_in_line.strip() == title_string.strip()):
                                # Whole title is a stop word (?) Somehow???
                                title_string = 'No title found'
                            else:
                                # Get title before the stop word
                                title_string = title_string.split(str(stop_word_in_line))[0]
                    # print(f"Possible title:\n{title_string}")
                    break
    # print(f"\nAbstract:\n {shortest_abstract}",flush=True)
    marc_record = marc_maker(important_ents, title_string, shortest_abstract, doc_path, document_patterns)
    return(marc_record)
