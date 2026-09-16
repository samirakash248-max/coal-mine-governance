import re

filepath = "frontend/src/pages/field/ReportEvent.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix VoiceRecorder component name or import
if "import { VoiceRecorder }" not in content:
    content = "import { VoiceRecorder } from '../../components/ui/VoiceRecorder';\n" + content

content = content.replace("onTranscriptionComplete={(t) =>", "onTranscriptionComplete={(t: string) =>")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
