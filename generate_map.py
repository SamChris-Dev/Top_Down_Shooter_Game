import xml.etree.ElementTree as ET
from xml.dom import minidom
import random

# Map dimensions
W = 20
H = 15

# Tile IDs (using what we saw in the contact sheets, offset by +1 for Tiled's GID system)
# Note: TMX uses 1-based indexing for the tileset
GRASS = 1   # tile_01
WOOD = 44   # tile_44
TILE_W = 12 # tile_12 (white tile)
WALL = 172  # tile_171 is dark grey with orange border, so gid=172

# Initialize arrays
floor_data = [GRASS] * (W * H)
wall_data = [0] * (W * H)

# Build the layout based on Sample.png
# House bounds: X: 4 to 15, Y: 3 to 13
house_x1, house_x2 = 4, 15
house_y1, house_y2 = 3, 13

# Interior room split (Bathroom at top right)
bath_x1, bath_x2 = 10, 15
bath_y1, bath_y2 = 3, 7

for y in range(H):
    for x in range(W):
        idx = y * W + x
        
        # Check if inside house
        if house_x1 <= x <= house_x2 and house_y1 <= y <= house_y2:
            # Check if bathroom
            if bath_x1 <= x <= bath_x2 and bath_y1 <= y <= bath_y2:
                floor_data[idx] = TILE_W
            else:
                floor_data[idx] = WOOD
                
            # Place walls on the perimeter of the house
            if x == house_x1 or x == house_x2 or y == house_y1 or y == house_y2:
                wall_data[idx] = WALL
                
            # Internal wall for bathroom
            if x == bath_x1 and bath_y1 <= y <= bath_y2:
                wall_data[idx] = WALL
            if y == bath_y2 and bath_x1 <= x <= bath_x2:
                wall_data[idx] = WALL

# Clear doors (openings in walls)
wall_data[8 * W + 4] = 0 # Front door (left)
wall_data[5 * W + 15] = 0 # Side door (right)
wall_data[7 * W + 12] = 0 # Bathroom door

# Generate XML
root = ET.Element("map", version="1.10", tiledversion="1.10.1", orientation="orthogonal", renderorder="right-down", width=str(W), height=str(H), tilewidth="64", tileheight="64", infinite="0", nextlayerid="4", nextobjectid="10")

# Add a giant tileset definition pointing to all individual tiles
tileset = ET.SubElement(root, "tileset", firstgid="1", name="Tiles", tilewidth="64", tileheight="64", tilecount="524", columns="0")
grid = ET.SubElement(tileset, "grid", orientation="orthogonal", width="1", height="1")
for i in range(1, 525):
    filename = f"tile_{i:02d}.png" if i < 100 else f"tile_{i}.png" # Handle naming convention
    # Try alternate if needed, but Tiled just stores the path string
    tile = ET.SubElement(tileset, "tile", id=str(i-1))
    ET.SubElement(tile, "image", width="64", height="64", source=f"PNG/Tiles/{filename}")

# Floor Layer
layer1 = ET.SubElement(root, "layer", id="1", name="Floors", width=str(W), height=str(H))
data1 = ET.SubElement(layer1, "data", encoding="csv")
data1.text = ",\n".join([",".join(map(str, floor_data[i*W:(i+1)*W])) for i in range(H)])

# Wall Layer
layer2 = ET.SubElement(root, "layer", id="2", name="Walls", width=str(W), height=str(H))
data2 = ET.SubElement(layer2, "data", encoding="csv")
data2.text = ",\n".join([",".join(map(str, wall_data[i*W:(i+1)*W])) for i in range(H)])

# Object Layer
objgroup = ET.SubElement(root, "objectgroup", id="3", name="Objects")

# Player
ET.SubElement(objgroup, "object", id="1", name="player", x="448", y="512", width="64", height="64")

# Zombies
ET.SubElement(objgroup, "object", id="2", name="zombie", x="128", y="128", width="64", height="64")
ET.SubElement(objgroup, "object", id="3", name="zombie", x="128", y="768", width="64", height="64")
ET.SubElement(objgroup, "object", id="4", name="zombie", x="1152", y="640", width="64", height="64")
ET.SubElement(objgroup, "object", id="5", name="zombie", x="1152", y="128", width="64", height="64")

# Collision Objects (Invisible Rectangles over walls)
obj_id = 6
for y in range(H):
    for x in range(W):
        if wall_data[y*W + x] != 0:
            ET.SubElement(objgroup, "object", id=str(obj_id), name="wall", x=str(x*64), y=str(y*64), width="64", height="64")
            obj_id += 1

xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent=" ")
with open("assets/map.tmx", "w") as f:
    f.write(xmlstr)
print("Map generated!")
