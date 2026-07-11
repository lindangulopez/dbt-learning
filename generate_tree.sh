#!/bin/bash
tree -a -I '.git|env|python_foundation|wallace|__pycache__|*.zip|*.tar.gz' > REPO_TREE.txt

echo "# Clean Repository Tree" > REPO_TREE.md
echo "" >> REPO_TREE.md
echo "\`\`\`" >> REPO_TREE.md
cat REPO_TREE.txt >> REPO_TREE.md
echo "\`\`\`" >> REPO_TREE.md
