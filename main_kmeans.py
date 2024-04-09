from flask import Flask, request, jsonify
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import seaborn as sns


app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False

data_frame = pd.read_csv('new_df2.csv')

data_frame.drop('Unnamed: 0', axis=1, inplace=True)

num_clusters = 6
kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0)

kmeans.fit(data_frame)

colors = ['#DF2020', '#81DF20', '#2095DF', '#FFA500', '#00FFFF', '#000000']
color_names = ['Red', 'Green', 'Blue', 'Orange', 'Cyan', 'Black']
cluster_colors = {i: (colors[i], color_names[i]) for i in range(num_clusters)}

columns_to_calculate = ["age", "sex", "size", "fixed", "house_trained", "special_needs", "shots_current",
                        "env_children", "env_dogs", "env_cats"]


def cluster_data(df):
    global num_clusters
    imputer = SimpleImputer(strategy='mean')
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    df_clustered = pd.DataFrame(df_imputed, columns=df.columns)

    df_clustered['cluster'] = KMeans(n_clusters=num_clusters).fit_predict(df_imputed)

    df_clustered.to_csv("data_frame_clustered.csv")

    print(silhouette_score(df_imputed, df_clustered['cluster']))
    print(davies_bouldin_score(df_imputed, df_clustered['cluster']))
    print(calinski_harabasz_score(df_imputed, df_clustered['cluster']))

    pca = PCA(n_components=3)
    data3D = pca.fit_transform(df_clustered.drop(columns=['cluster']))

    # Print the columns contributing to each principal component
    print("Columns contributing to each principal component:")
    for i, comp in enumerate(pca.components_, 1):
        print(f"PCA Component {i}:")
        for j, weight in enumerate(comp):
            print(f" {df.columns[j]}: {weight}")

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

    for column in df_clustered.columns:
        if column != 'cluster':
            cluster_percentages = df_clustered.groupby('cluster')[column].value_counts(normalize=True).unstack()

            fig, ax = plt.subplots(figsize=(10, 8))
            neutral_colors = ['#7B68EE', '#FF6347', '#FFD700', '#9ACD32']
            cluster_percentages.plot(kind='bar', stacked=True, ax=ax, color=neutral_colors)
            plt.title(f'Stacked Percentage Bar Graph for {column}')
            plt.ylabel('Percentage')
            plt.xlabel('Cluster')

            ax.set_xticks(range(num_clusters))
            ax.set_xticklabels([cluster_colors[i][1] for i in range(num_clusters)])

            plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
            plt.show()

    def plot_absolute_counts(df, num_clusters):
        for column in df.columns:
            if column != 'cluster':
                # Define a list of specific colors in HEX code for each cluster
                palette = ['#DF2020', '#81DF20', '#2095DF', '#FFA500', '#00FFFF', '#000000']

                plt.figure(figsize=(10, 8))
                ax = sns.countplot(x=column, hue='cluster', data=df, palette=palette)
                plt.title(f'Absolute Counts of {column} Across Clusters')
                plt.xlabel(column)
                plt.ylabel('Count')

                custom_labels = ['Red', 'Green', 'Blue', 'Orange', 'Cyan', 'Black']
                plt.legend(title='Cluster', labels=custom_labels)

                for p in ax.patches:
                    if p.get_height() > 0:
                        ax.text(p.get_x() + p.get_width() / 2., p.get_height(),
                                '{:1.0f}'.format(p.get_height()),
                                fontsize=12, color='black', ha='center', va='bottom')

                plt.show()

    plot_absolute_counts(df_clustered, 6)

    def plot_distributions(df, num_clusters, cluster_names):
        for column in df.columns:
            if column != 'cluster':
                # Calculate the distribution of each unique value across clusters
                distribution = df.groupby('cluster')[column].value_counts(normalize=True).unstack()

                # Plot the distribution
                plt.figure(figsize=(10, 8))
                ax = sns.heatmap(distribution, annot=True, fmt=".2%", cmap="YlGnBu", cbar=False,
                                 yticklabels=cluster_names)
                plt.title(f'Distribution of {column} Across Clusters')
                plt.ylabel('Cluster')
                plt.xlabel(column)

                plt.show()

    cluster_names = ['Red', 'Green', 'Blue', 'Orange', 'Cyan', 'Black']
    plot_distributions(df_clustered, num_clusters, cluster_names)

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
