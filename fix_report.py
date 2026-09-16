import re

filepath = "frontend/src/pages/field/ReportEvent.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
content = content.replace("import { Button } from '../../components/ui/button';", "import { Button } from '../../components/ui/button';\nimport { VoiceRecorder } from '../../components/ui/VoiceRecorder';")

# Add Voice Recorder next to Description label
target = """<label className="block text-sm font-medium text-gray-700">Description</label>"""
replacement = """<div className="flex justify-between items-center"><label className="block text-sm font-medium text-gray-700">Description</label><VoiceRecorder onTranscriptionComplete={(t) => setDescription(prev => prev + " " + t)} /></div>"""
content = content.replace(target, replacement)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
