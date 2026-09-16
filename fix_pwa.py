import re

filepath = "frontend/vite.config.ts"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_pwa = """    VitePWA({ 
      registerType: 'autoUpdate', 
      manifest: { 
        name: 'CoalCore', 
        short_name: 'CoalCore', 
        theme_color: '#0f172a', 
        icons: [] 
      } 
    })"""
new_pwa = """    VitePWA({ 
      registerType: 'autoUpdate', 
      workbox: {
        cleanupOutdatedCaches: true,
        clientsClaim: true,
        skipWaiting: true
      },
      manifest: { 
        name: 'CoalCore', 
        short_name: 'CoalCore', 
        theme_color: '#0f172a', 
        icons: [] 
      } 
    })"""
content = content.replace(old_pwa, new_pwa)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
