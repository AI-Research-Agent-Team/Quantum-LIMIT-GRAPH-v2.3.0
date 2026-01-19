# Terminal 1: Start green agent
python server.py

# Terminal 2: Start baseline purple agent
python baseline_purple_agent/simple_agent.py

# Terminal 3: Test evaluation
python -c "
import requests
import json

# Send assessment request to green agent
response = requests.post('http://localhost:8000/v1/tasks', json={
    'participants': {
        'test_agent': 'http://localhost:8001'
    },
    'config': {
        'test_suites': ['multilingual']
    }
})

print(json.dumps(response.json(), indent=2))
"
