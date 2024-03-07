from flask import Flask, request, jsonify
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap


app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False

data_frame = pd.read_csv('new_df.csv')

scaler = StandardScaler()
scaler.fit(data_frame)


def cluster_data(df):
    df_scaled = scaler.transform(df)
    imputer = SimpleImputer(strategy='mean')
    df_imputed = pd.DataFrame(imputer.fit_transform(df_scaled), columns=df.columns)
    num_clusters = 6
    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0).fit(df_imputed)
    df_clustered = pd.DataFrame(df_imputed, columns=df.columns)
    df_clustered['cluster'] = kmeans.labels_

    pca = PCA(n_components=3)
    data3D = pca.fit_transform(df_clustered.drop(columns=['cluster']))

    fig = plt.figure(figsize=(20, 12))
    ax = fig.add_subplot(111, projection='3d')  # Correctly create a 3D subplot

    cmap = get_cmap('tab20')
    colors = [cmap(i) for i in range(num_clusters)]
    for i, color in enumerate(colors):
        cluster_points = data3D[df_clustered['cluster'] == i]
        ax.scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2], color=color)

    ax.set_xlabel('PCA Component 1')
    ax.set_ylabel('PCA Component 2')
    ax.set_zlabel('PCA Component 3')
    plt.title('Clusters Visualization in 3D')
    plt.show()

    return df_clustered


@app.route('/add_data', methods=['POST'])
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
    app.run()
