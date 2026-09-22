import re

filepath = "frontend/src/components/ui/TeamAccessManager.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove 'React' from import
content = content.replace('import React, { useState, useEffect } from "react";', 'import { useState, useEffect } from "react";')

# 2. Remove 'User', 'ShieldAlert', 'UserCog' from lucide-react import
# Original: import { User, Shield, ShieldAlert, CheckCircle2, XCircle, MoreHorizontal, UserCog, UserX, Loader2 } from "lucide-react";
content = content.replace('import { Shield, CheckCircle2, XCircle, MoreHorizontal, UserX, Loader2 } from "lucide-react";', 'import { Shield, CheckCircle2, XCircle, MoreHorizontal, UserX, Loader2 } from "lucide-react";')
# Actually let's just do a regex sub for the lucide-react import to only include used ones.
import_pattern = r'import \{([^}]+)\} from "lucide-react";'
def fix_lucide_imports(match):
    imports = [x.strip() for x in match.group(1).split(',')]
    for unused in ['User', 'ShieldAlert', 'UserCog']:
        if unused in imports:
            imports.remove(unused)
    return 'import { ' + ', '.join(imports) + ' } from "lucide-react";'

content = re.sub(import_pattern, fix_lucide_imports, content)

# 3. Remove getRoleBadgeVariant and formatRoleName functions
# We will just remove the entire blocks.
block_getRoleBadgeVariant = r'  const getRoleBadgeVariant = \(role: Role\) => \{.*?\};\n\n'
content = re.sub(block_getRoleBadgeVariant, '', content, flags=re.DOTALL)

block_formatRoleName = r'  const formatRoleName = \(role: string\) => \{.*?\};\n\n'
content = re.sub(block_formatRoleName, '', content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
