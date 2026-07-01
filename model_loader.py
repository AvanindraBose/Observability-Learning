import seaborn as sns
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df = sns.load_dataset('iris')

# encoding categorical column: Species
def encoder(species):
    if species == "setosa":
        return 0
    elif species == "versicolor":
        return 1
    else:
        return 2

df['encode_species'] = df['species'].apply(encoder)

df.drop(columns=['species'],inplace=True)

X = df.drop(columns=['encode_species'])
y = df['encode_species']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42) 

rf = RandomForestClassifier()

trained_model = rf.fit(X_train,y_train)

joblib.dump(trained_model,'trained_mode.joblib')


