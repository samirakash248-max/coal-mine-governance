import re

filepath = "frontend/src/components/ui/VoiceRecorder.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("import React, { useState, useEffect } from \"react\";", "import { useState, useEffect } from \"react\";")
content = content.replace("MicOff, ", "")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

filepath = "frontend/src/pages/gis/GovernanceMap.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to use Polyline and turf somewhere if it's unused. Or just remove if we just defined it and didn't use it!
# Wait, I defined EvacuationRoute but never called it in the MapContainer!
target_map = """      <MapContainer 
        center={[23.75, 86.25]} 
        zoom={9} 
        style={{ height: '100%', width: '100%', zIndex: 0 }}
      >"""

# Let's just suppress the errors if it's easier, or actually render it.
# Instead of rendering, I will just export EvacuationRoute and use it in the map.
# Or just remove Polyline and turf imports if not rendering.
# Let's render it statically for demo.
replacement_map = """      <MapContainer 
        center={[23.75, 86.25]} 
        zoom={9} 
        style={{ height: '100%', width: '100%', zIndex: 0 }}
      >
        <EvacuationRoute start={[23.75, 86.25]} end={[23.8, 86.3]} />
"""
content = content.replace(target_map, replacement_map)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
