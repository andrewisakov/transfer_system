import yaml

config = yaml.safe_load(open('app/core/database.yaml'))
INIT = config.get('init')
DSN = config.get('dsn')
