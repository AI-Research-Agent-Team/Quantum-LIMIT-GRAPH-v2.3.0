# client/a2a_client.py
"""A2A Client for communicating with purple agents"""

import aiohttp
from typing import Dict, Any

class PurpleAgentProxy:
    """Proxy for purple agent A2A communication"""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    async def query(self, text: str) -> str:
        """Send query to purple agent"""
        async with aiohttp.ClientSession() as session:
            # Send A2A task
            async with session.post(
                f"{self.endpoint}/v1/tasks",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "parts": [{"type": "text", "text": text}]
                        }
                    ]
                }
            ) as resp:
                result = await resp.json()
                task_id = result.get("task_id")
            
            # Get result
            async with session.get(
                f"{self.endpoint}/v1/tasks/{task_id}"
            ) as resp:
                result = await resp.json()
                
                # Extract response text
                for msg in result.get("messages", []):
                    for part in msg.get("parts", []):
                        if part.get("type") == "text":
                            return part.get("text", "")
                
                return ""


class A2AClient:
    """A2A protocol client"""
    
    def create_proxy(self, endpoint: str) -> PurpleAgentProxy:
        """Create purple agent proxy"""
        return PurpleAgentProxy(endpoint)
