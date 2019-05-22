import math
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import pandas as pd
import seaborn as sns

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier , GradientBoostingClassifier

# Modelling Helpers
from sklearn.preprocessing import Imputer , Normalizer , scale
from sklearn.model_selection import train_test_split , StratifiedKFold
from sklearn.feature_selection import RFECV

import warnings
warnings.filterwarnings('ignore')


def plot_correlation_map( df ):
    corr = df.corr()
    _ , ax = plt.subplots( figsize =( 12 , 10 ) )
    cmap = sns.diverging_palette( 220 , 10 , as_cmap = True )
    _ = sns.heatmap(
        corr, 
        cmap = cmap,
        square=True, 
        cbar_kws={ 'shrink' : .9 }, 
        ax=ax, 
        annot = True, 
        annot_kws = { 'fontsize' : 12 }
    )

def plot_distribution( df , var , target , **kwargs ):
    row = kwargs.get( 'row' , None )
    col = kwargs.get( 'col' , None )
    facet = sns.FacetGrid( df , hue=target , aspect=4 , row = row , col = col )
    facet.map( sns.kdeplot , var , shade= True )
    facet.set( xlim=( 0 , df[ var ].max() ) )
    facet.add_legend()

def plot_categories( df , cat , target , **kwargs ):
    row = kwargs.get( 'row' , None )
    col = kwargs.get( 'col' , None )
    facet = sns.FacetGrid( df , row = row , col = col )
    facet.map( sns.barplot , cat , target )
    facet.add_legend()

def plot_variable_importance( X , y ):
    tree = DecisionTreeClassifier( random_state = 99 )
    tree.fit( X , y )
    plot_model_var_imp( tree , X , y )

def plot_model_var_imp( model , X , y ):
    imp = pd.DataFrame( 
        model.feature_importances_  , 
        columns = [ 'Importance' ] , 
        index = X.columns 
    )
    imp = imp.sort_values( [ 'Importance' ] , ascending = True )
    imp[ : 10 ].plot( kind = 'barh' )
    print (model.score( X , y ))


# train = pd.read_csv("./datasets/train.csv")
# train.describe()
# plot_correlation_map( train )
# plot_distribution( train , var = 'Age' , target = 'Survived' , row = 'Sex' )
# plot_distribution( train , var = 'Fare' , target = 'Survived')
# plot_categories( train , cat = 'Pclass' , target = 'Survived' )
# sns.heatmap(train.isnull(),yticklabels=False, cbar=False, cmap='YlGnBu')


def preprocessing():
    train = pd.read_csv("./datasets/train.csv")
    test = pd.read_csv("./datasets/test.csv")
    full = train.append( test , ignore_index = True )

    # print(full.head(1000))

    sex = pd.Series( np.where( full.Sex == 'male' , 1 , 0 ) , name = 'Sex' )
    embarked = pd.get_dummies( full.Embarked , prefix='Embarked' )
    pclass = pd.get_dummies( full.Pclass , prefix='Pclass' )

    imputed = pd.DataFrame()
    imputed[ 'Age' ] = full.Age.fillna( full.Age.mean() )
    imputed[ 'Fare' ] = full.Fare.fillna( full.Fare.mean() )


    title = pd.DataFrame()
    # extract the title from each name
    title[ 'Title' ] = full[ 'Name' ].map( lambda name: name.split( ',' )[1].split( '.' )[0].strip() )
    
    Title_Dictionary = {
                    "Capt":       "Officer",
                    "Col":        "Officer",
                    "Major":      "Officer",
                    "Jonkheer":   "Royalty",
                    "Don":        "Royalty",
                    "Sir" :       "Royalty",
                    "Dr":         "Officer",
                    "Rev":        "Officer",
                    "the Countess":"Royalty",
                    "Dona":       "Royalty",
                    "Mme":        "Mrs",
                    "Mlle":       "Miss",
                    "Ms":         "Mrs",
                    "Mr" :        "Mr",
                    "Mrs" :       "Mrs",
                    "Miss" :      "Miss",
                    "Master" :    "Master",
                    "Lady" :      "Royalty"

                    }

    title[ 'Title' ] = title.Title.map( Title_Dictionary )
    title = pd.get_dummies( title.Title )
    # print(title.head())



    cabin = pd.DataFrame()
    # replacing missing cabins with Unknown
    cabin[ 'Cabin' ] = full.Cabin.fillna( 'Unknown' )
    # mapping each Cabin value with the cabin letter(First character)
    cabin[ 'Cabin' ] = cabin[ 'Cabin' ].map( lambda c : c[0] )
    # dummy encoding ...
    cabin = pd.get_dummies( cabin['Cabin'] , prefix = 'Cabin' )


    # a function that extracts each prefix of the ticket, returns 'XXX' if no prefix (i.e the ticket is a digit)
    def cleanTicket( ticket ):
        ticket = ticket.replace( '.' , '' )
        ticket = ticket.replace( '/' , '' )
        ticket = ticket.split()
        ticket = map( lambda t : t.strip() , ticket )
        ticket = list(filter( lambda t : not t.isdigit() , ticket ))
        if len( ticket ) > 0:
            return ticket[0]
        else: 
            return 'XXX'

    ticket = pd.DataFrame()
    # Extracting dummy variables from tickets:
    ticket[ 'Ticket' ] = full[ 'Ticket' ].map( cleanTicket )
    ticket = pd.get_dummies( ticket[ 'Ticket' ] , prefix = 'Ticket' )



    family = pd.DataFrame()
    # introducing a new feature : the size of families (including the passenger)
    family[ 'FamilySize' ] = full[ 'Parch' ] + full[ 'SibSp' ] + 1
    # introducing other features based on the family size
    family[ 'Family_Single' ] = family[ 'FamilySize' ].map( lambda s : 1 if s == 1 else 0 )
    family[ 'Family_Small' ]  = family[ 'FamilySize' ].map( lambda s : 1 if 2 <= s <= 4 else 0 )
    family[ 'Family_Large' ]  = family[ 'FamilySize' ].map( lambda s : 1 if 5 <= s else 0 )

    # full_X = pd.concat( [ sex, embarked, pclass, imputed, cabin, title, ticket, family ] , axis=1 )
    full_X = pd.concat( [ sex, embarked, pclass, imputed, cabin, title, family ] , axis=1 )
    X_train = full_X[0:891]
    Y_train = train.Survived
    X_test = full_X[891:]
    
    Y_test = pd.read_csv("./datasets/answer.csv")
    Y_test = Y_test.survived
    Y_test = Y_test[891:]

    return X_train, Y_train, X_test, Y_test
    

X_train, Y_train, X_test, Y_test = preprocessing()
# plot_variable_importance(X_train, Y_train)

# model = RandomForestClassifier(n_estimators=100)
# model = SVC()
# model = GradientBoostingClassifier()
# model = KNeighborsClassifier(n_neighbors = 3)
# model = GaussianNB()
model = LogisticRegression()

model.fit( X_train , Y_train )

print (model.score( X_train , Y_train ))
print (model.score( X_test , Y_test ))
# plot_model_var_imp(model, X_train, Y_train)



"""
full_X = pd.concat( [ sex, embarked, pclass, imputed, cabin, title, family ] , axis=1 )
train and test set accuracy for models

RandomForestClassifier
0.9876543209876543
0.5454545454545454

SVC
0.856341189674523
0.5287081339712919

GradientBoostingClassifier
0.9057239057239057
0.5669856459330144

KNeighborsClassifier
0.8484848484848485
0.5502392344497608

GaussianNB
0.8002244668911336
0.4784688995215311

LogisticRegression
0.8395061728395061
0.5430622009569378
"""

