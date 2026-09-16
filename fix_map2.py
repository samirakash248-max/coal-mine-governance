import re

filepath = "frontend/src/pages/gis/GovernanceMap.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
if "import * as turf" not in content:
    content = content.replace("import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';", "import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';\nimport * as turf from '@turf/turf';")

# Let's find where we map mines and add evacuation route for a dummy "critical hazard" if it exists.
# We will just export a dummy EvacuationRoute component and add it to the map.

new_component = """
function EvacuationRoute({ start, end }: { start: [number, number], end: [number, number] }) {
  // Simple straight line for demo. In a real app, turf.shortestPath or pgRouting would be used.
  const line = turf.lineString([
    [start[1], start[0]],
    [end[1], end[0]]
  ]);
  
  // Create a slight curve to make it look like a path
  const curved = turf.bezierSpline(line);
  const coords = curved.geometry.coordinates.map(c => [c[1], c[0]] as [number, number]);

  return <Polyline positions={coords} color="red" dashArray="5, 10" weight={4} />;
}
"""

if "function EvacuationRoute" not in content:
    content = content.replace("export default function GovernanceMap", new_component + "\nexport default function GovernanceMap")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
