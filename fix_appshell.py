import re

filepath = "frontend/src/layouts/AppShell.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                  <div className="h-8 w-8 rounded-full bg-earth-200 flex items-center justify-center text-earth-800 font-bold text-sm">
                    {userProfile?.first_name?.[0] || ''}{userProfile?.last_name?.[0] || 'U'}
                  </div>
                  <span className="text-sm font-medium text-graphite-700 hidden sm:block">
                    {userProfile ? `${userProfile.first_name} ${userProfile.last_name}` : 'Loading...'}
                  </span>"""

replacement = """                  <div className="h-8 w-8 rounded-full bg-earth-200 flex items-center justify-center text-earth-800 font-bold text-sm">
                    {userProfile?.full_name ? userProfile.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <span className="text-sm font-medium text-graphite-700 hidden sm:block">
                    {userProfile?.full_name || 'Loading...'}
                  </span>"""

content = content.replace(target, replacement)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
