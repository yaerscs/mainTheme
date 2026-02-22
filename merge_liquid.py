import re
import json

working_file = 'sections/main-product.liquid'
broken_file = 'main/sections/main-product.liquid'

def extract_schema(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    schema_start = content.find('{% schema %}')
    schema_end = content.find('{% endschema %}')
    
    if schema_start == -1 or schema_end == -1:
        return None
        
    schema_json_str = content[schema_start + 12:schema_end].strip()
    return json.loads(schema_json_str), content[:schema_start], content[schema_end+13:]

working_schema, working_top, working_bottom = extract_schema(working_file)
broken_schema, broken_top, broken_bottom = extract_schema(broken_file)

# Find blocks in broken that aren't in working
working_block_types = [b.get('type') for b in working_schema.get('blocks', [])]
blocks_to_add = []

for block in broken_schema.get('blocks', []):
    btype = block.get('type')
    # Filter out Kaching-breaking blocks
    if btype not in working_block_types and btype not in ['buy_buttons', 'variant_picker', 'quantity_selector', 'kaching_bundles_app_block']:
        blocks_to_add.append(block)

print(f"Adding {len(blocks_to_add)} blocks to schema: {[b.get('type') for b in blocks_to_add]}")

working_schema['blocks'].extend(blocks_to_add)

# Now we need to update the top part where the blocks are rendered
# We will find the {% case block.type %} and insert the rendering code for our new blocks.
# A naive approach is to just extract the `{% when 'product_faq' %}` etc from broken_top and inject it

new_liquid_code = ""
for b in blocks_to_add:
    btype = b.get('type')
    # Find the block rendering in broken_top
    start_tag = f"{{%- when '{btype}' -%}}"
    if start_tag not in broken_top:
        start_tag = f"{{% when '{btype}' %}}"
        
    if start_tag in broken_top:
        start_idx = broken_top.find(start_tag)
        # Find the next when statement or endcase
        next_when = broken_top.find("{%- when", start_idx + 10)
        next_when_2 = broken_top.find("{% when", start_idx + 10)
        next_endcase = broken_top.find("{%- endcase -%}", start_idx + 10)
        
        # Determine the earliest end of this block
        ends = [e for e in [next_when, next_when_2, next_endcase] if e != -1]
        if ends:
            end_idx = min(ends)
            block_code = broken_top[start_idx:end_idx]
            new_liquid_code += block_code + "\n"

# Inject into working_top right before {%- endcase -%}
if new_liquid_code:
    endcase_idx = working_top.rfind("{%- endcase -%}")
    if endcase_idx != -1:
        working_top = working_top[:endcase_idx] + new_liquid_code + working_top[endcase_idx:]

# Write the new file
new_schema_str = json.dumps(working_schema, indent=2)
new_content = working_top + "{% schema %}\n" + new_schema_str + "\n{% endschema %}\n" + working_bottom

with open('sections/main-product.liquid', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Liquid merge complete.")
