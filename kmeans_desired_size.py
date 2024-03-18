# -*- coding: utf-8 -*-
"""KMeans_desired_size.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q2CUXp_IIyB8Qmj81rSwtYwdbQ4PeJvv

**let's clone the repo.**
"""

!git clone https://github.com/Carriot-Tech/data-scientist-challenge.git

# Commented out IPython magic to ensure Python compatibility.
# %cd data-scientist-challenge

"""**load data and libraries**"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import cm, colors

points = pd.read_csv("/content/data-scientist-challenge/test.csv")
clusters = np.load("/content/data-scientist-challenge/cluster_sizes.npy")
df = points[["Geo location latitude","Geo location longitude" ]]

clusters.shape

df.describe()

df.info()

"""**visualize data**"""

latitude =  points["Geo location latitude"]
longitude =  points["Geo location longitude"]

plt.scatter(longitude, latitude, color='blue', marker='o')
plt.title('Points')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.show()

!pip install folium

"""**lets see it in a map**"""

import folium

# Create a folium map centered at an initial location
mymap = folium.Map(location=[df['Geo location latitude'].mean(), df['Geo location longitude'].mean()], zoom_start=4)

# Add markers for each row in the DataFrame
for index, row in df.iterrows():
    folium.Marker(location=[row['Geo location latitude'], row['Geo location longitude']], popup=str(index)).add_to(mymap)

# Display the map
mymap

"""**Algorithms:**

there are many ways to solve the problem. the main problem is to minimize the size of distance from points to their centers which we can consider it as a eror. this method is much works like K_Means algorithm which is a popular method Machin Learning.

there are many ways to solve the problem but we use **2 algorithm** which have diffrence outputs.

**first algorithm:**

in this algorithm we assign points to centers untill the size of centers be full.
"""

print(np.newaxis)

class KMeansByGroup:
    def __init__(self, clusters):
        self.num_centers = len(clusters)
        self.initial_centroids = None
        self.num_members_per_center = None
        self.max_iterations = None
        self.final_centroids = None
        self.final_assignments = None

    def assign_points_to_centers(self, data, centroids, num_members):
        num_points = data.shape[0]
        num_centers = centroids.shape[0]
        # Compute distance matrix between all points and all centers
        distances = np.linalg.norm(data.values[:, np.newaxis, :] - centroids, axis=2)
        # distances = distances**2
        # Initialize a list to store assigned points and their corresponding center indices
        assigned_points = []
        # Assign points to centers based on the specified number of members
        for k in range(num_centers):

            # Get the indices of the k nearest points to the current center
            center_distances = distances[:, k]
            sorted_indices = np.argsort(center_distances)
            # Select the first k points that have not been assigned yet
            selected_indices = sorted_indices[:num_members[k]]
            # Store the assigned points and their center index
            assigned_points.extend([(point_index, k) for point_index in selected_indices])
            # Update distances by setting distances of assigned points to infinity
            distances[selected_indices, :] = np.inf

        return np.array(assigned_points)

    def update_centroids(self, data, old_centroids, assignments):
        K = old_centroids.shape[0]
        centroids = []

        for k in range(K):
            # collect indices of points belonging to kth cluster
            S_k = np.argwhere(assignments[:, 1] == k).flatten()

            # take average of points belonging to this cluster
            if len(S_k) > 0:
                c_k = np.mean(data.iloc[S_k, :].values, axis=0)
            else:  # what if no points in the cluster? keep the previous centroid
                c_k = np.copy(old_centroids[k, :])
            centroids.append(c_k)

        return np.array(centroids)

    def my_kmeans(self, data, centroids, max_its, num_members_per_center):
        # outer loop - alternate between updating assignments / centroids
        for j in range(max_its):

            # update cluster assignments
            assignments = self.assign_points_to_centers(data, centroids, num_members_per_center)
            # update centroid locations
            centroids = self.update_centroids(data, centroids, assignments)

        # final assignment update
        assignments = self.assign_points_to_centers(data, centroids, num_members_per_center)
        return centroids, assignments

    def fit(self, data, clusters, max_iterations):
        self.initial_centroids = np.random.uniform(low=-50, high=50, size=(self.num_centers, 2))
        self.num_members_per_center = clusters
        self.max_iterations = max_iterations

        self.final_centroids, self.final_assignments = self.my_kmeans(
            data, self.initial_centroids, self.max_iterations, self.num_members_per_center
        )

    def get_final_centroids(self):
        return self.final_centroids

    def get_final_assignments(self):
        return self.final_assignments


max_iterations = 10
kmeans = KMeansByGroup(clusters)
kmeans.fit(df, clusters, max_iterations)
final_centroids = kmeans.get_final_centroids()
final_assignments = kmeans.get_final_assignments()

cluster_df = pd.DataFrame(final_assignments, columns=['Index', 'Cluster'])
result_df = cluster_df.groupby('Cluster')['Index'].agg(list).reset_index()
result_df.columns = ['Cluster', 'Indices']

# Display the resulting DataFrame
print(result_df)
print("Final Centroids (latitude, longitude):")
print(final_centroids)
print("Final Assignments:")
print(result_df)

"""**restructuring outout to requested restructuring**"""

# mange the output to save in csv as requested
output = result_df
for index, row in output.iterrows():

    indices_list = row['Indices']
    lat_lon_list = []
    for index_val in indices_list:
        lat_val = df.loc[index_val, 'Geo location latitude']
        lon_val = df.loc[index_val, 'Geo location longitude']
        lat_lon_list.append((lat_val, lon_val))
    output.at[index, 'Indices'] = lat_lon_list
output.to_csv('/content/data-scientist-challenge/output1.csv', index=False)
output.head()

"""**visulize results**"""

# Create a new map centered on a specific location
m = folium.Map(location=[0, 0], zoom_start=2)

# Generate a colormap with the number of clusters
num_clusters = len(output)
colormap = cm.get_cmap('tab20', num_clusters)

# Plot each cluster
for i, row in output.iterrows():
    cluster_id = row['Cluster']
    points = row['Indices']

    # Create a feature group for the cluster
    cluster_fg = folium.FeatureGroup(name=f'Cluster {cluster_id}')

    # Generate a color for the cluster
    color = colors.rgb2hex(colormap(cluster_id % num_clusters))

    # Plot each point in the cluster
    for point in points:
        # Extract latitude and longitude
        lat, lon = point

        # Create a marker for the point and add it to the feature group
        folium.CircleMarker(location=[lat, lon], color=color, fill=True, fill_color=color, fill_opacity=0.7).add_to(cluster_fg)

    # Add the feature group to the map
    cluster_fg.add_to(m)

# Add a layer control to the map
folium.LayerControl().add_to(m)
m.save('/content/data-scientist-challenge/cluster_map1.html')
# Display the map
m

!pip install folium

"""**second algorithm**"""

import folium

class KMeansByCenter:
    def __init__(self, num_clusters, max_iterations):
        self.num_clusters = num_clusters
        self.max_iterations = max_iterations

    def assign_points_to_clusters(self, centroids, points, cluster_sizes):
        num_clusters = len(centroids)
        num_points = len(points)
        cluster_assignments = [[] for _ in range(num_clusters)]
        assigned_points = set()

        for cluster_idx in range(num_clusters):
            centroid = centroids[cluster_idx]
            cluster_size = cluster_sizes[cluster_idx]

            # Calculate Euclidean distances between centroid and points
            distances = np.linalg.norm(points - centroid, axis=1)
            # distnaces = distances**4
            # Sort distances and get the indices of the nearest points
            nearest_indices = np.argsort(distances)

            # Assign points to the cluster until it reaches the desired size
            assigned_points_cluster = 0
            point_idx = 0
            while assigned_points_cluster < cluster_size and point_idx < num_points:
                point = nearest_indices[point_idx]
                if point not in assigned_points:
                    cluster_assignments[cluster_idx].append(point)
                    assigned_points.add(point)
                    assigned_points_cluster += 1
                point_idx += 1

        total_elements = sum(len(sublist) for sublist in cluster_assignments)

        # Create an empty NumPy array of the required shape
        result = np.zeros((total_elements, 2), dtype=int)

        # Fill the array with the numbers and their corresponding indices
        current_index = 0
        for i, sublist in enumerate(cluster_assignments):
            for num in sublist:
                result[current_index] = [num, i]
                current_index += 1

        return result


    def update_centroids(self, data, old_centroids, assignments):
        K = old_centroids.shape[0]
        centroids = []

        for k in range(K):
            # collect indices of points belonging to kth cluster
            S_k = np.argwhere(assignments[:, 1] == k).flatten()

            # take average of points belonging to this cluster
            if len(S_k) > 0:
                c_k = np.mean(data.iloc[S_k, :].values, axis=0)
            else:  # what if no points in the cluster? keep the previous centroid
                c_k = np.copy(old_centroids[k, :])
            centroids.append(c_k)

        return np.array(centroids)

    def fit(self, data, cluster_sizes):
        num_centers = self.num_clusters
        initial_centroids = np.random.uniform(low=-50, high=50, size=(num_centers, 2))
        num_members_per_center = cluster_sizes

        centroids = initial_centroids
        assignments = None

        # Outer loop - alternate between updating assignments / centroids
        for _ in range(self.max_iterations):
            # Update cluster assignments
            assignments = self.assign_points_to_clusters(centroids, data, num_members_per_center)
            # Update centroid locations
            centroids = self.update_centroids(data, centroids, assignments)

        return centroids, assignments

kmeans = KMeansByCenter(num_clusters=len(clusters), max_iterations=1)
final_centroids2, final_assignments2= kmeans.fit(df, clusters)

cluster_df = pd.DataFrame(final_assignments2, columns=['Index', 'Cluster'])
result_df2 = cluster_df.groupby('Cluster')['Index'].agg(list).reset_index()
result_df2.columns = ['Cluster', 'Indices']

# Display the resulting DataFrame
print(result_df2)
print("Final Centroids (latitude, longitude):")
print(final_centroids2)
print("Final Assignments:")
print(result_df2)

output2 = result_df2
for index, row in output2.iterrows():

    indices_list = row['Indices']
    lat_lon_list = []
    for index_val in indices_list:
        lat_val = df.loc[index_val, 'Geo location latitude']
        lon_val = df.loc[index_val, 'Geo location longitude']
        lat_lon_list.append((lat_val, lon_val))
    output2.at[index, 'Indices'] = lat_lon_list
output2.to_csv('/content/data-scientist-challenge/output2.csv', index=False)
output2.head()

import folium
import matplotlib.cm as cm
import matplotlib.colors as colors

# Create a new map centered on a specific location
m = folium.Map(location=[0, 0], zoom_start=2)

# Generate a colormap with the number of clusters
num_clusters = len(output2)
colormap = cm.get_cmap('tab20', num_clusters)

# Plot each cluster
for i, row in output2.iterrows():
    cluster_id = row['Cluster']
    points = row['Indices']

    # Create a feature group for the cluster
    cluster_fg = folium.FeatureGroup(name=f'Cluster {cluster_id}')

    # Generate a color for the cluster
    color = colors.rgb2hex(colormap(cluster_id % num_clusters))

    # Plot each point in the cluster
    for point in points:
        # Extract latitude and longitude
        lat, lon = point

        # Create a marker for the point and add it to the feature group
        folium.CircleMarker(location=[lat, lon], color=color, fill=True, fill_color=color, fill_opacity=0.7).add_to(cluster_fg)

    # Add the feature group to the map
    cluster_fg.add_to(m)

# Add a layer control to the map
folium.LayerControl().add_to(m)
m.save('/content/data-scientist-challenge/cluster_map2.html')
# Display the map
m

"""**which algorithm is better?**

it is based on our problem but second algorithm may have better results.

**are there any other way?**

yes, we can use the "for" loop on our points not the centers. it may works better, but as mentioned it is based on our problem.

there are too many ways to solve problems.
"""

