PirateSearchEngine

Made by: [Leonardo Louis Gutierrez IV, Ashar Huda, Adam Gans, Samuel Mallari]

The purpose of this project was to emulate a scalable search engine that could be used in relation to our previous assignment 2 crawler. Though with
this project, we use a preset model of urls and their respective contents to search though. Our search engine makes use of various data structures,
such as an inverted index, to store the urls and their contents. From the invertedIndex, it creates multiple files to use for the search engine.
The index relies on postings lists to store for tokens and relies on SimHashing to get rid of duplicate url contents both near and exact. We also tokenize
the contents and rely on the Porter Stemmer to stem the tokens. We also use the PageRank algorithm to rank the urls based on their importance.

On a fresh run of the index, the index will take several hours to run because of SimHashing. When scaling we would usually pick a different similarity method,
that would save on both memory and time for the machine, but for now we use SimHashing to go through about 55k urls.

***The main reason for files is to offload the memory usage of the inverted index.***

The files made from the index are:
- highest_pagerank.txt -> contains mapping of docs to their pagerank in descending order
- highest_tf_idf.txt -> contains mapping of docs to their tf-idf in descending order
- inverted_index.txt -> contains mapping of words with list of docs they appear in, their word count, their tf-idf, fields, and positions
- page_rank.txt -> contains mapping of docs to their pagerank
- token_positions_list.txt -> contains mapping of words with their positions in the docs
- top_words.txt -> contains the top words in the index by word count
- total_tfidf.txt -> contains total tf-idf
- url_dict.txt -> contains mapping of doc_id to url

With these files made from the index folder files, we use these to search for the top 10 urls that match any query.
The files we use are all stored on the root directory of the project. And all content we use from DEV so far is all ICS related because of the assignment.
The search engine can be used by either the query.py or queryGUI.py files. The query.py file is the same as the queryGUI.py file, but without the GUI.

IMPORTANT: to run the queryGUI.py file, you must have the required libraries installed. The required libraries are located in the requirements.txt file. You must also
run the file in a special way, "streamlit run queryGUI.py". This is because the file uses the streamlit library to create the GUI.

Without any of these files, the search engine will not work so make sure to have them all in the root directory of the project.

Extra Credit that was done:
- GUI for the search engine
- PageRank algorithm
- SimHashing (exact and near duplicates)
- OpenAI summarization API
- Index Anchor Texts
- Implement Word Positions
- ML model to get best values for search engine (non-graded but Adam liked it)

HOW TO RUN:
- To run the search engine, you must first build the index from the invertedIndex.py file.
- Then with those files now in the root directory, you can run either query.py or queryGUI.py to search with queries.
- BOOM! You now have a search engine that can search through the ICS related urls we have stored in the index.
