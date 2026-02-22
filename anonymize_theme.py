import os

def replace_in_files(directory):
    for root, dirs, files in os.walk(directory):
        if 'main' in root.split(os.sep): 
            continue # skip the 'main' old directory just in case
            
        for file in files:
            if file.endswith(('.liquid', '.json', '.css')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if 'shrine' in content.lower():
                        # Safe case-preserving replacement
                        new_content = content.replace('Shrine', 'Rapid')
                        new_content = new_content.replace('shrine', 'rapid')
                        new_content = new_content.replace('SHRINE', 'RAPID')
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            print(f"Updated {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

dirs_to_process = ['layout', 'sections', 'snippets', 'templates', 'config', 'locales']

for d in dirs_to_process:
    if os.path.exists(d):
        replace_in_files(d)

print("Replacement complete. Skipped assets/ where JS logic resides.")
