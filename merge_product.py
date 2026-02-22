import json

working_file = "product_working_utf8.json"
broken_file = "product_broken.json"

with open(working_file, 'r', encoding='utf-8') as f:
    text = f.read()
    json_start = text.find('{')
    working_data = json.loads(text[json_start:])

with open(broken_file, 'r', encoding='utf-8') as f:
    text = f.read()
    json_start = text.find('{')
    broken_data = json.loads(text[json_start:])

working_main = working_data['sections']['main']
broken_main = broken_data['sections']['main']

# Exclude all custom blocks from the broken theme that interfere or don't exist in working schema
conflict_blocks = ["buy_buttons", "variant_picker", "quantity_selector", "kaching_bundles_app_block"]

merged_blocks = working_main.get('blocks', {})
merged_order = working_main.get('block_order', [])

for block_id, block_data in broken_main.get('blocks', {}).items():
    is_conflict = False
    for conflict in conflict_blocks:
        if conflict in block_id or conflict in block_data.get('type', ''):
            is_conflict = True
            break
            
    if not is_conflict and block_id not in merged_blocks:
        merged_blocks[block_id] = block_data
        if block_id not in merged_order:
            merged_order.append(block_id)

working_data['sections']['main']['blocks'] = merged_blocks
working_data['sections']['main']['block_order'] = merged_order

# Entirely new sections
for sec_id, sec_data in broken_data.get('sections', {}).items():
    if sec_id != 'main' and sec_id not in working_data['sections']:
        working_data['sections'][sec_id] = sec_data

working_order = working_data.get('order', [])
for sec_id in broken_data.get('order', []):
    if sec_id not in working_order:
        working_order.append(sec_id)
working_data['order'] = working_order

with open("templates/product.json", "w", encoding="utf-8") as f:
     json.dump(working_data, f, indent=2)

print("Merge complete")
