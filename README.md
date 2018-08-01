# Language Identification and Named Entity Recognition in Hinglish Code Mixed Tweets
Kushagra Singh, Indira Sen, Ponnurangam Kumaraguru <br />
ACL 2018, SRW <br />

Repository contains<br />
(i)   Seq2seq based transliterator (Roman to Devanagri)<br />
(ii)  Language identification tool for Hindi-English code switched text (English, Hindi, Rest)<br />
(iii) CRF based Named Entity Recogntion tool for Hindi-English code switched text (Person, Location, Organisation)<br />
<br />

Check http://precog.iiitd.edu.in/resources.html for the annotated corpus.

- Install dependencies using requirements.txt file in a virtualenv. <br />
- Check the README in transliteration dir and follow instructions to set up. <br />

- Export the following env variables before running demo files <br />
~~~~
export TRANSLITERATION_DIR={{path_to_parent_dir}}/hindi-english-code-mixing-lidf-ner/transliteration
export HINGLISH_ROOT_DIR={{path_to_parent_dir}}/hindi-english-code-mixing-lidf-ner
~~~~
