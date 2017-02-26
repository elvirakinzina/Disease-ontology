# Disease-ontology
The Telegram [DOID bot] (http://t.me/doidbot) is a tool for unification of terms in medical diagnoses.

# Description
It utilizes The Ontology Lookup Service ([OLS] (http://www.ebi.ac.uk/ols/index)) which is developed and maintained by EMBL-EBI. It also checks for typos and abbreviations and looks for synonyms of initial terms from term associations in scientific and medical papers from [PubMed] (https://www.ncbi.nlm.nih.gov/pubmed) and [Wikipedia] (https://www.wikipedia.org) if ontologies for initial terms could not be identified.

The exact scheme of work is represented in the picture below.

![alt text](https://github.com/elliekinz/Disease-ontology/blob/master/images/Scheme_eng.png)

# Usage
You can find examples to check the bot on in the data folder. It would look like this:

`#` Reason for admission: Cardiomyopathy

`#` Acute infarction (localization): no

`#` Former infarction (localization): no

`#` Additional diagnoses: Hypertrophic obstructive cardiomyopathy

Or simply type any medical diagnostic term, for example, "aortic stenosis".
