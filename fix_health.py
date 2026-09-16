import re

filepath = "frontend/src/pages/HealthCheck.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove useMock import and setup
content = re.sub(r'const \[useMock, setUseMock\] = useState\(false\);\n', '', content)
content = re.sub(r'const { data, loading, error, refetch } = useApi<HealthResponse>\(\'/health\', { immediate: !useMock }\);', r"const { data, loading, error, refetch } = useApi<HealthResponse>('/health');", content)

# Remove mockData object completely
content = re.sub(r'const mockData: HealthResponse = \{.*?\};\n', '', content, flags=re.DOTALL)

# Replace healthData logic
content = content.replace("const healthData = useMock ? mockData : data;", "const healthData = data;")

# Remove useMock from conditions
content = content.replace("if (!useMock) {", "if (true) {")
content = content.replace("disabled={loading && !useMock}", "disabled={loading}")
content = content.replace("loading && !useMock", "loading")
content = content.replace("error && !useMock", "error")
content = content.replace("? !useMock :", "? false :")

# Remove the Use Mock checkbox UI
checkbox_ui = r'<label className="flex items-center gap-2 text-sm text-graphite-600">\s*<input[^>]+>\s*Use Mock Data\s*</label>'
content = re.sub(checkbox_ui, '', content, flags=re.IGNORECASE)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
