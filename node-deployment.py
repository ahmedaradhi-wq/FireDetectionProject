import numpy as np
from shapely.geometry import Polygon, Point
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import folium

# -----------------------------------------------------------
# 1. DEFINE YOUR POLYGON (Zeytinpark approximation)
# -----------------------------------------------------------
polygon_coords = [
    (30.657042, 36.932945 ),
    (30.664651, 36.925716),
    (30.659399, 36.916533),
    (30.646653, 36.917048),
    (30.645151, 36.927855),
    (30.648498, 36.931423)
]
poly = Polygon(polygon_coords)

# -----------------------------------------------------------
# 2. GENERATE GRID OF CANDIDATE POINTS INSIDE POLYGON
# -----------------------------------------------------------
def generate_grid_points(polygon, spacing_m=50):
    """
    Generate a grid of candidate points inside the polygon.
    spacing_m = approx spacing in meters
    """
    # Approx conversion: 1 deg latitude ≈ 111,320 m
    lat_spacing = spacing_m / 111320
    # 1 deg longitude ≈ 111320 * cos(latitude)
    mean_lat = np.mean([p[1] for p in polygon.exterior.coords])
    lon_spacing = spacing_m / (111320 * np.cos(np.radians(mean_lat)))

    minx, miny, maxx, maxy = polygon.bounds
    x_vals = np.arange(minx, maxx, lon_spacing)
    y_vals = np.arange(miny, maxy, lat_spacing)

    points = []
    for x in x_vals:
        for y in y_vals:
            p = Point(x, y)
            if polygon.contains(p):
                points.append([x, y])
    return np.array(points)

candidate_points = generate_grid_points(poly, spacing_m=50)
print(f"Number of candidate points: {len(candidate_points)}")

# -----------------------------------------------------------
# 3. K-MEANS CLUSTERING TO SELECT 80 NODES
# -----------------------------------------------------------
NODE_COUNT = 80
kmeans_nodes = KMeans(n_clusters=NODE_COUNT, random_state=42)
node_labels = kmeans_nodes.fit_predict(candidate_points)
node_positions = kmeans_nodes.cluster_centers_
print(f"Selected {len(node_positions)} node positions.")

# -----------------------------------------------------------
# 4. K-MEANS CLUSTERING TO SELECT 16 CLUSTER HEADS
# -----------------------------------------------------------
CH_COUNT = 16
kmeans_ch = KMeans(n_clusters=CH_COUNT, random_state=42)
ch_labels = kmeans_ch.fit_predict(node_positions)
ch_positions = kmeans_ch.cluster_centers_

# Assign each node to nearest CH
from scipy.spatial import distance_matrix
D = distance_matrix(node_positions, ch_positions)
node_ch_assignment = np.argmin(D, axis=1) + 1  # CH IDs from 1 to 16

# -----------------------------------------------------------
# 5. MATPLOTLIB VISUALIZATION
# -----------------------------------------------------------
plt.figure(figsize=(8, 8))
# Draw polygon
x, y = poly.exterior.xy
plt.plot(x, y, 'black', linewidth=2)
# Draw nodes
plt.scatter(node_positions[:, 0], node_positions[:, 1], c='blue', s=20, label="Nodes")
# Draw CHs
plt.scatter(ch_positions[:, 0], ch_positions[:, 1], c='red', s=200, marker='X', label="Cluster Heads")
# Draw lines node → CH
for i in range(len(node_positions)):
    n = node_positions[i]
    c = ch_positions[node_ch_assignment[i]-1]
    plt.plot([n[0], c[0]], [n[1], c[1]], color='gray', linewidth=0.5)

plt.title("Evenly Distributed Nodes with Cluster Heads")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid(True)
plt.show()

# -----------------------------------------------------------
# 6. INTERACTIVE MAP WITH FOLIUM
# -----------------------------------------------------------
map_center = [np.mean([p[1] for p in polygon_coords]), np.mean([p[0] for p in polygon_coords])]
m = folium.Map(location=map_center, zoom_start=15)

# Polygon
folium.Polygon(
    locations=[(lat, lon) for lon, lat in polygon_coords],
    color="black",
    weight=3,
    fill=False
).add_to(m)

# Nodes and lines
for i in range(len(node_positions)):
    n_lon, n_lat = node_positions[i]
    c_lon, c_lat = ch_positions[node_ch_assignment[i]-1]

    # Line from node → CH
    folium.PolyLine(
        locations=[(n_lat, n_lon), (c_lat, c_lon)],
        color="gray",
        weight=1
    ).add_to(m)

    # Node marker
    folium.CircleMarker(
        location=(n_lat, n_lon),
        radius=3,
        color="blue",
        fill=True
    ).add_to(m)

# Cluster heads markers
for i, center in enumerate(ch_positions):
    folium.Marker(
        location=(center[1], center[0]),
        popup=f"Cluster Head {i+1}",
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

# Save interactive map
m.save("clusters_map.html")
print("Interactive map saved as: clusters_map.html")