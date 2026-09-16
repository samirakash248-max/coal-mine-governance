import re

filepath = "frontend/src/pages/gis/GovernanceMap.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';", "import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';")
content = content.replace("import * as turf from '@turf/turf';", "")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
