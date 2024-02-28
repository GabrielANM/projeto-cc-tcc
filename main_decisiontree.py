from flask import Flask, request, jsonify
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False

data_frame = pd.read_csv('df_dogs58k.csv')
# data_frame = pd.read_csv('df_dogs_without_nan2.csv')


# target_column = 'coat'
target_column = 'breed_primary'

X = data_frame.drop(columns=[target_column])
y = data_frame[target_column]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)


def classify_data(df):
    missing_columns = set(X.columns) - set(df.columns)
    for col in missing_columns:
        df[col] = 0

    df = df[X.columns]

    new_data_class = dt_model.predict(df)
    df['predicted_class'] = new_data_class
    return df


@app.route('/add_data3', methods=['POST'])
def add_data():
    global data_frame
    new_data = request.json
    new_row = pd.DataFrame([new_data])

    data_frame = pd.concat([data_frame, new_row], ignore_index=True)

    classified_df = classify_data(data_frame)

    new_row_predicted_class = classified_df.iloc[-1]['predicted_class']

    matching_rows = classified_df[classified_df['predicted_class'] == new_row_predicted_class].drop(
        columns=['predicted_class'])

    num_matching_rows = len(matching_rows)

    return jsonify({
        'matching_rows': matching_rows.to_dict(orient='records'),
        'num_matching_rows': num_matching_rows
    })


if __name__ == '__main__':
    app.run(debug=True)
