from database import get_db
from config_model import Config

# Get database session
db = next(get_db())

# Check LLM configs
print('LLM configs:')
llm_configs = db.query(Config).filter(Config.category == 'llm').all()
for config in llm_configs:
    print(f'  {config.key}: {config.value}')

# Check all configs
print('\nAll configs:')
all_configs = db.query(Config).all()
for config in all_configs:
    print(f'  {config.key} (category: {config.category}): {config.value}')

# Check if any configs exist
print(f'\nTotal configs: {len(all_configs)}')
print(f'Total LLM configs: {len(llm_configs)}')
