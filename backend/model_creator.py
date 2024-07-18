import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.ensemble import VotingClassifier
import joblib

# THis file is used to create the AI model based on the change in location, device, time and attempts to decide whether login attempt is safe or not

current_dir = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(current_dir, "dataset.csv"))

df = df.drop(columns=["id"])

X = df.drop(columns=["safe"])
y = df["safe"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model1 = xgb.XGBClassifier(eval_metric="logloss", random_state=42)
model2 = RandomForestClassifier(n_estimators=100, random_state=42)

model = VotingClassifier(estimators=[("xgb", model1), ("rf", model2)], voting="soft")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

joblib.dump(model, "secure_auth_ai_model.pkl")
