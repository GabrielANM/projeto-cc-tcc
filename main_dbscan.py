from flask import Flask, request, jsonify
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.impute import SimpleImputer

app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False

data_frame = pd.read_csv('df_dogs_without_nan2.csv')


def cluster_data(df):
    imputer = SimpleImputer(strategy='mean')

    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

    dbscan = DBSCAN(eps=0.5, min_samples=5)
    df_imputed['cluster'] = dbscan.fit_predict(df_imputed)

    return df_imputed


@app.route('/add_data4', methods=['POST'])
def add_data():
    global data_frame
    new_data = request.json
    new_row = pd.DataFrame([new_data])

    data_frame = pd.concat([data_frame, new_row], ignore_index=True)

    clustered_df = cluster_data(data_frame)

    new_row_cluster = clustered_df.iloc[-1]['cluster']

    matching_rows = clustered_df[clustered_df['cluster'] == new_row_cluster].drop(columns=['cluster'])

    num_matching_rows = len(matching_rows)

    return jsonify({
        'matching_rows': matching_rows.to_dict(orient='records'),
        'num_matching_rows': num_matching_rows
    })


if __name__ == '__main__':
    app.run(debug=True)