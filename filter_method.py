# -*- coding: utf-8 -*-
"""Filter_Method.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1f4A4fewAjsEwEsjNr48z_SUJ9TVszPQo
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
#from sklearn.feature_extraction.text import TfidfVectorizer

#NLTK-------------------------------
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
#from nltk.stemporter import PorterStemmer

# Import libraries for feature 
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix,classification_report
from sklearn import metrics
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings("ignore")

from google.colab import drive
drive.mount('/gdrive')
#Change current working directory to gdrive
# %cd /gdrive

#Read files
textfile = r'/gdrive/My Drive/CIS 508/Assignment/HW5/Comments.csv'
textData = pd.read_csv(textfile) #creates a dataframe

CustInfofile = r'/gdrive/My Drive/CIS 508/Assignment//HW5/Customers.csv'
CustInfoData = pd.read_csv(CustInfofile)  #creates a dataframe

print(textData.shape)
print(CustInfoData.shape)

#Extract target column from Customer Info file
y_train = CustInfoData["TARGET"]
X_train = CustInfoData.drop(columns=["TARGET"]) #extracting training data without the target column
                     
print(X_train.shape)
print(textData.shape)
textData.head()
print(y_train)

# Use English stemmer.
stemmer = SnowballStemmer("english")
#Tokenize - Split the sentences to lists of words
textData['CommentsTokenized'] = textData['Comments'].apply(word_tokenize)

#export_csv = textData.to_csv(r'/gdrive/My Drive/CIS 508/Assignment/HW5/TextDataTokenized.csv')

#Now do stemming - create a new dataframe to store stemmed version
newTextData=pd.DataFrame()
newTextData=textData.drop(columns=["CommentsTokenized","Comments"])
newTextData['CommentsTokenizedStemmed'] = textData['CommentsTokenized'].apply(lambda x: [stemmer.stem(y) for y in x]) # Stem every word.

#export_csv = newTextData.to_csv(r'/gdrive/My Drive/CIS 508/Assignment/HW5/newTextDataTS.csv')

#Join stemmed strings
newTextData['CommentsTokenizedStemmed'] = newTextData['CommentsTokenizedStemmed'].apply(lambda x: " ".join(x))

export_csv = newTextData.to_csv(r'/gdrive/My Drive/CIS 508/Assignment/HW5/newTextData-Joined.csv')

#Do Bag-Of-Words model - Term - Document Matrix
#Learn the vocabulary dictionary and return term-document matrix.
#count_vect = CountVectorizer(stop_words=None)
count_vect = CountVectorizer(stop_words='english',lowercase=False)
TD_counts = count_vect.fit_transform(newTextData.CommentsTokenizedStemmed)
print(TD_counts.shape)
TD_counts.dtype
print(count_vect.get_feature_names())
#print(TD_counts)
DF_TD_Counts=pd.DataFrame(TD_counts.toarray())
#print(DF_TD_Counts)
export_csv = DF_TD_Counts.to_csv(r'/gdrive//My Drive/CIS 508/Assignment/HW5/TD_counts-TokenizedStemmed.csv')

#Compute TF-IDF Matrix
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(TD_counts)
print(X_train_tfidf.shape)
DF_TF_IDF=pd.DataFrame(X_train_tfidf.toarray())
print(DF_TF_IDF)
export_csv= DF_TF_IDF.to_csv(r'/gdrive/My Drive/CIS 508/Assignment/HW5/TFIDF_counts-TokenizedStemmed.csv')

#Feature selection
new_DF_TF_IDF = SelectKBest(score_func=chi2, k=50).fit_transform(DF_TF_IDF,y_train)
new_DF_TF_IDF.shape

DF_TF_IDF_SelectedFeatures= pd.DataFrame(new_DF_TF_IDF)
print(DF_TF_IDF_SelectedFeatures)

export_csv= DF_TF_IDF_SelectedFeatures.to_csv(r'/gdrive//My Drive/CIS 508/Assignment/HW5/TFIDF_counts-Selected Features.csv')

#Construct a Random Forest Classifier on text data
clf=RandomForestClassifier()
RF_text = clf.fit(DF_TF_IDF_SelectedFeatures,y_train)
print("Accuracy score (training): {0:.6f}".format(clf.score(DF_TF_IDF_SelectedFeatures, y_train)))
rf_predictions = clf.predict(DF_TF_IDF_SelectedFeatures)
print("Confusion Matrix:")
print(confusion_matrix(y_train, rf_predictions))
print("Classification Report")
print(classification_report(y_train, rf_predictions))

#Merge files
print(CustInfoData.shape)
X_train = CustInfoData.drop(columns=["TARGET"]) #extracting training data without the target column
print(X_train.shape)
combined=pd.concat([X_train, DF_TF_IDF_SelectedFeatures], axis=1)
print(combined.shape)
print(combined)
export_csv= combined.to_csv(r'/gdrive/My Drive/CIS 508/Assignment/HW5/Combined-Cust+TFIDF+SelectedFeatures.csv')

#Do one Hot encoding for categorical features
X_cat = ["Sex","Status","Car_Owner","Paymethod","LocalBilltype","LongDistanceBilltype"]
#X_cat = combined.select_dtypes(exclude=['int','float64'])
print(X_cat)
combined_one_hot = pd.get_dummies(combined,columns=X_cat)
print(combined_one_hot.shape)
export_csv= combined_one_hot.to_csv(r'/gdrive/My Drive/CIS 508/Assignment/HW5/combined_one_hot.csv')

X = combined_one_hot
y_train = CustInfoData["TARGET"]

print (X.shape)
print (y_train.shape)

X_train, X_test, y_train, y_test = train_test_split(X,y_train, test_size = 0.2, random_state= 42)

#Construct a Random Forest Classifier on combined data
#clf1=RandomForestClassifier()
RF_Comb = clf.fit(X_train,y_train)
# print("Accuracy score (training): {0:.6f}".format(clf.score(X_train, y_train)))
rf_predictions = clf.predict(X_test)
print("Accuracy score (training): {0:.6f}".format(clf.score(X_test, y_test)))
print("Confusion Matrix:")
print(confusion_matrix(y_test, rf_predictions))
print("Classification Report")
print(classification_report(y_test, rf_predictions))