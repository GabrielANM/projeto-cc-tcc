from flask import Flask, request, jsonify
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False

data_frame = pd.read_csv('new_df.csv')

data_frame.drop('Unnamed: 0', axis=1, inplace=True)

num_clusters = 8
kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0)

kmeans.fit(data_frame)

colors = ['#DF2020', '#81DF20', '#2095DF', '#FFA500', '#00FFFF', '#000000', '#FF00FF', '#00FF00']
color_names = ['Red', 'Green', 'Blue', 'Orange', 'Cyan', 'Black', 'Magenta', 'Lime']
cluster_colors = {i: (colors[i], color_names[i]) for i in range(num_clusters)}

columns_to_calculate = ["age", "sex", "size", "fixed", "house_trained", "special_needs", "shots_current",
                        "env_children", "env_dogs", "env_cats"]


def cluster_data(df):
    global num_clusters
    imputer = SimpleImputer(strategy='mean')
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    df_clustered = pd.DataFrame(df_imputed, columns=df.columns)

    df_clustered['cluster'] = kmeans.predict(df_imputed)

    pca = PCA(n_components=3)
    data3D = pca.fit_transform(df_clustered.drop(columns=['cluster']))

    fig = plt.figure(figsize=(20, 12))
    ax = fig.add_subplot(111, projection='3d')

    for i in range(num_clusters):
        cluster_points = data3D[df_clustered['cluster'] == i]
        color, color_name = cluster_colors[i]
        ax.scatter(cluster_points[:, 0], cluster_points[:, 1], cluster_points[:, 2], color=color, alpha=0.6,
                   s=10, label=color_name)

    ax.set_xlabel('PCA Component 1')
    ax.set_ylabel('PCA Component 2')
    ax.set_zlabel('PCA Component 3')
    plt.title('Clusters Visualization in 3D')

    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    plt.show()

    for cluster in range(num_clusters):
        cluster_rows = df_clustered[df_clustered['cluster'] == cluster].drop(columns=['cluster'])
        cluster_percentages = {}

        for column in columns_to_calculate:
            if column in cluster_rows.columns:
                cluster_percentages[column] = cluster_rows[column].value_counts(normalize=True).to_dict()

        cluster_percentages_df = pd.DataFrame(cluster_percentages).T

        cluster_percentages_df.plot(kind='bar', stacked=True, figsize=(10, 8))
        color, color_name = cluster_colors[cluster]
        plt.title(f'Stacked Percentage Bar Graph for {color_name} Cluster')
        plt.ylabel('Percentage')
        plt.xlabel('Category')
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
        plt.show()

    last_row_cluster = df_clustered.iloc[-1]['cluster']
    cluster_name = cluster_colors[last_row_cluster][1]

    return df_clustered, cluster_name


@app.route('/add_data', methods=['POST'])
def add_data():
    global data_frame
    new_data = request.json
    new_row = pd.DataFrame([new_data])

    data_frame = pd.concat([data_frame, new_row], ignore_index=True)
    clustered_df = cluster_data(data_frame)
    new_row_cluster = clustered_df[0].iloc[-1]['cluster']
    matching_rows = clustered_df[0][clustered_df[0]['cluster'] == new_row_cluster].drop(columns=['cluster'])
    num_matching_rows = len(matching_rows)

    columns_to_calc = ["age", "sex", "size", "fixed", "house_trained", "special_needs", "shots_current",
                       "env_children", "env_dogs", "env_cats"]

    cluster_percentages = {}

    for cluster in range(num_clusters):
        cluster_rows = clustered_df[0][clustered_df[0]['cluster'] == cluster].drop(columns=['cluster'])

        cluster_percentages[cluster_colors[cluster][1]] = {}

        for column in columns_to_calc:
            if column in cluster_rows.columns:
                cluster_percentages[cluster_colors[cluster][1]][column] = cluster_rows[column].value_counts(
                    normalize=True).to_dict()

    return jsonify({
        'matching_rows': matching_rows.to_dict(orient='records'),
        'num_matching_rows': num_matching_rows,
        'column_frequencies_percentage': cluster_percentages,
        'new_row_cluster_name': cluster_colors[new_row_cluster][1]
    })


if __name__ == '__main__':
    app.run()
