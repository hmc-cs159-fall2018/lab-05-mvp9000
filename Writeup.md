1. In general, Laplace smoothing exists in order to make the model more generalizable by adding to the counts and preventing zeroes in denominators. In the EditDistance.py, Laplace smoothing is implemented by adding 0.1 to all the counts in the counts dictionary. Without laplace smoothing we could end up with zero probabilities for a given intended and observed character. This could lead to problems when computing alignment probability.
2. python3 EditDistance.py --store ed.pkl --source ../data/spelling/wikipedia\_misspellings.txt
3. The LanguageModel class only supports unigrams and bigrams.
4. To deal with zero counts of unigrams and bigrams, the LanguageModel class adds self.alpha to both the numerator and denominator
5. The \_\_contains\_\_ function is not meant to be called directly; rather, it allows us to use keywords like "in" to check if an element is present.
6. The get\_chunks method takes a list of filenames and the chunksize, then iterates across the filesyielding chunk\_size many lines of each file.
7. python3 LanguageModel.py /data/gutenberg/\*.txt -s lm.plk -a 0.1 -v 40000 
8. Our `spellchecker` created more errors than it helped. The issue is that our vocabulary of 40000 is too small. A lot of valid words are treated as misspelled words and then corrected to something else. At times the correction distorts the meaning of the sentence (changing relevant to irrelevant). So most of the modifications our spell checker makes leads to creating an error and only occasionally does it fix a genuine mistake. Considering that our spellchecker did worse than the original text, it did a lot worse than ispell.
9. One place we improved upon ispell is since we always lowercase words we don't unnecessarily change cases of words (although that are times where a case change is desired that we'll never make). Beyond that while we never noticed any spelling corrections that our model improved on relative to ispell. ispell is better at contractions as the current word tokenization from spacy breaks up don't into two wordsand trys spell checking each piece. 
10. Our current way of processing punctuation leads to them being ignored by the language model. Another annoyance is that after tokenization it's messy to get the text back with the corrections since your tokenization algorithm would have needed to have kept track of any white space. The vocab size for ispell looks to be around 100k words based on looking for the dict file I think it uses. That's much larger than the vocab size for our language model. I also think proper spell checking needs to better detect things like named entities as those will always be difficult to have captured in the vocabulary. We tried to increase our vocab size, but that was unsuccessful as the training data did not even have 50k unique words. Also the training data for the language model itself had typos so some of our vocabulary is incorrect itself.
11. We decided to do the real-world correction option. Our approach included allowing our spellchecker model to consider corrections for every single word of a sentence. To accomplish this, when we generated candidates for every word, we made sure not to remove the word for which we were correcting if that was a word in the language model. 
12. A few examples of how the new model (bottom) compares to the baseline spellchecker (top) are below:

**She** stuck her nose where it does n't belong . I believe the argument was between me and Yvesnimmo . But like I said , the situation was settled and **I** apologized

\-\-\-

**he** stuck her nose where it does n't belong . i believe the argument was between me and Yvesnimmo . but like i said , the situation was settled and **a** apologized 


**your** vandalism to the at Shirvington article has been reverted . Please do n't do it again , or you will be banned .

\-\-\-

**our** vandalism to the at Shirvington article has been reverted . please do n't do it again , or you will be banned .

ABC officially says THIS is the name for that episode . I do know there is already an episode with that name , but ABC says it 's " Everybod
y 's **Says** Do n't " .

\-\-\-

ABC officially says THIS is the name for that episode . i do know there is already an episode with that name , but ABC says it 's " everybod
y 's **ways** o n't "

13. The code changes were not as substantial as the conceptual change. Our main practical issue was that using the language model actually creates morerrors and adds bias to our spelling correction as now words like 'she' may be corrected to 'he' because our language model finds 'he' more likely.
