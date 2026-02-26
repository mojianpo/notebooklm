from database import get_db
from routers.content import get_llm_config

# Get database session
db = next(get_db())

# Test get_llm_config function
print('Testing get_llm_config...')
config = get_llm_config(db)
print('Result:')
for key, value in config.items():
    print(f'  {key}: {value}')

# Check if API key is present
print(f'\nAPI key found: {"api_key" in config and config["api_key"]}')
print(f'Model found: {"model" in config and config["model"]}')
print(f'Base URL found: {"base_url" in config and config["base_url"]}')
