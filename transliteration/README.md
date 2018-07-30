Seq2Seq model for transliterating Roman text into Devanagari text. Uses Google Seq2Seq 

Requires tensoflow==1.1.0

Step 1. Setup transliteration requirements by using requirements.txt <br />
Step 2. Change 'vocab\_target' and 'vocab\_source' file path prefix in transliterationModel/train\_options.json to local paths<br />

Check out demo.py for a running example. Delete wordsToTransliterate.txt and wordsTransliterated.txt before running. <br />

export TRANSLITERATION\_DIR={{local path to repo}}/Hindi\_English\_Code\_Switching\_Tools/transliteration <br />
