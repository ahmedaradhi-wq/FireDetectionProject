# ===================================================================================
#IoT Sensor Deployment & Coverage Analysis for Zeytinpark

#Author: Ahmed Ali
#ahmed.a.radhi@nahrainuniv.edu.iq
#Description:
#This script generates sensor node locations inside a park using K-Means clustering,
#assigns Cluster Heads (CHs), visualizes the network on an interactive map,
#and calculates the coverage percentage of the park.

##Technologies:
#- NumPy
#- Shapely (GIS operations)
#- Scikit-learn (KMeans clustering)
#- Folium (interactive maps)
#- SciPy (distance calculations)
#- Pandas (data export)
# ====================================================================================

import numpy as np
from shapely.geometry import Polygon, Point
from sklearn.cluster import KMeans
import folium
from scipy.spatial import distance_matrix
import pandas as pd

# =====================================================
# 1. Define Zeytinpark Boundary (Longitude, Latitude)
# =====================================================
polygon_coords = [
    (30.657042, 36.932945),
    (30.664651, 36.925716),
    (30.659399, 36.916533),
    (30.646653, 36.917048),
    (30.645151, 36.927855),
    (30.648498, 36.931423)
]

# Create polygon object for spatial operations
poly = Polygon(polygon_coords)

# =====================================================
# 2. Generate Grid Points Inside the Park
# =====================================================
def generate_grid_points(polygon, spacing_m=50):
    """
    Generate evenly spaced grid points within a polygon.

    Args:
        polygon (Polygon): Target area
        spacing_m (float): Distance between points in meters

    Returns:
        np.array: Points inside the polygon (lon, lat)
    """

    # Convert spacing from meters to degrees (approximation)
    lat_spacing = spacing_m / 111320
    mean_lat = np.mean([p[1] for p in polygon.exterior.coords])
    lon_spacing = spacing_m / (111320 * np.cos(np.radians(mean_lat)))

    # Get bounding box of polygon
    minx, miny, maxx, maxy = polygon.bounds
    points = []

    # Generate grid and keep only points inside polygon
    for x in np.arange(minx, maxx, lon_spacing):
        for y in np.arange(miny, maxy, lat_spacing):
            p = Point(x, y)
            if polygon.contains(p):
                points.append([x, y])

    return np.array(points)

# Generate candidate points inside the park
candidate_points = generate_grid_points(poly, spacing_m=50)

# =====================================================
# 3. Select 80 Sensor Nodes using K-Means
# =====================================================
NODE_COUNT = 80

# Apply clustering to distribute nodes evenly
kmeans_nodes = KMeans(n_clusters=NODE_COUNT, random_state=42)
node_labels = kmeans_nodes.fit_predict(candidate_points)

# Extract node positions (cluster centers)
node_positions = kmeans_nodes.cluster_centers_

# =====================================================
# 4. Select 16 Cluster Heads (CHs)
# =====================================================
CH_COUNT = 16

# Cluster nodes again to define CH locations
kmeans_ch = KMeans(n_clusters=CH_COUNT, random_state=42)
ch_labels = kmeans_ch.fit_predict(node_positions)

# Extract CH positions
ch_positions = kmeans_ch.cluster_centers_

# Assign each node to the nearest CH
D = distance_matrix(node_positions, ch_positions)
node_ch_assignment = np.argmin(D, axis=1) + 1  # CH IDs start from 1

# =====================================================
# 5. Save Node and CH Data to CSV
# =====================================================

# Save node data
nodes_df = pd.DataFrame({
    "Node_ID": np.arange(1, NODE_COUNT + 1),
    "Longitude": node_positions[:, 0],
    "Latitude": node_positions[:, 1],
    "Assigned_CH": node_ch_assignment
})
nodes_df.to_csv(r"C:\Users\ahmed\Desktop\nodes_positions.csv", index=False)
print("Nodes positions saved in nodes_positions.csv")

# Save cluster head data
ch_df = pd.DataFrame({
    "CH_ID": np.arange(1, CH_COUNT + 1),
    "Longitude": ch_positions[:, 0],
    "Latitude": ch_positions[:, 1]
})
ch_df.to_csv(r"C:\Users\ahmed\Desktop\cluster_heads_positions.csv", index=False)
print("Cluster Heads positions saved in cluster_heads_positions.csv")

# =====================================================
# 6. Create Interactive Map
# =====================================================

# Compute map center
map_center = [
    np.mean([p[1] for p in polygon_coords]),
    np.mean([p[0] for p in polygon_coords])
]

# Initialize map
m = folium.Map(location=map_center, zoom_start=15)

# Draw park boundary
folium.Polygon(
    locations=[(lat, lon) for lon, lat in polygon_coords],
    color="black",
    weight=3,
    fill=False
).add_to(m)

# Coverage radius for each sensor (in meters)
coverage_radius_m = 100

# =====================================================
# 6.1 Plot Nodes, Links, and Coverage
# =====================================================
for i, node in enumerate(node_positions):
    n_lon, n_lat = node
    c_lon, c_lat = ch_positions[node_ch_assignment[i] - 1]

    # Draw connection line (Node → Cluster Head)
    folium.PolyLine(
        locations=[(n_lat, n_lon), (c_lat, c_lon)],
        color="gray",
        weight=1
    ).add_to(m)

    # Draw node point
    folium.CircleMarker(
        location=(n_lat, n_lon),
        radius=3,
        color="blue",
        fill=True
    ).add_to(m)

    # Draw coverage circle
    folium.Circle(
        location=(n_lat, n_lon),
        radius=coverage_radius_m,
        color="blue",
        fill=True,
        fill_opacity=0.1
    ).add_to(m)

# Draw Cluster Heads
for i, ch in enumerate(ch_positions):
    folium.Marker(
        location=(ch[1], ch[0]),
        popup=f"Cluster Head {i+1}",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

# =====================================================
# 7. Calculate Coverage Percentage
# =====================================================
from shapely.ops import unary_union

# Convert radius to degrees (approximate conversion)
mean_lat = np.mean(node_positions[:, 1])
radius_deg = coverage_radius_m / (111320 * np.cos(np.radians(mean_lat)))

coverage_polygons = []

# Create circular buffers for each node
for node in node_positions:
    lon, lat = node
    circle = Point(lon, lat).buffer(radius_deg)
    coverage_polygons.append(circle)

# Merge all coverage areas into one geometry
coverage_union = unary_union(coverage_polygons)

# Compute overlap between coverage and park
intersection = coverage_union.intersection(poly)

# Calculate percentage of covered area
coverage_percent = (intersection.area / poly.area) * 100

print(f"Coverage Percentage: {coverage_percent:.2f}%")

# =====================================================
# 8. Save Interactive Map
# =====================================================
m.save("zeytinpark_iot_map_with_coverage.html")
print("Interactive IoT map with coverage saved.")