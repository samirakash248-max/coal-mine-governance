import re

filepath = "frontend/src/pages/gis/GovernanceMap.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add apiClient import if not present
if "import { apiClient }" not in content:
    content = content.replace("import { useState, useEffect } from 'react';", "import { useState, useEffect } from 'react';\nimport { apiClient } from '../../api/client';")

old_hook = """// A dummy hook for weather risk since it's requested to stub it
function useWeatherRisk(mineId: string) {
  const [risk, setRisk] = useState<string>('Loading...');
  
  useEffect(() => {
    if (!mineId) return;
    setRisk('Loading...');
    fetch(`/api/v1/weather/risk/${mineId}`)
      .then(res => res.json())
      .then(data => setRisk(data?.level || 'MODERATE'))
      .catch(() => setRisk('MODERATE'));
  }, [mineId]);
  
  return risk;
}"""

new_hook = """function useWeatherRisk(mineId: string) {
  const [risk, setRisk] = useState<string>('Loading...');
  
  useEffect(() => {
    if (!mineId) return;
    setRisk('Loading...');
    apiClient.get(`/weather/risk/${mineId}`)
      .then(res => setRisk(res.data?.level || 'MODERATE'))
      .catch(() => setRisk('MODERATE'));
  }, [mineId]);
  
  return risk;
}"""

content = content.replace(old_hook, new_hook)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
