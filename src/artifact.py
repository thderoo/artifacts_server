import secrets
import os
import json
import datetime
import asyncio

artifact_buffer = {}

artifact_dict = None
artifact_dict_lock = asyncio.Lock()

fields = ['id', 'token', 'name', 'content', 'created_at', 'modified_at']

class Artifact:
    def __init__(self, name: str, content: str):
        used_artifact = True
        while used_artifact:
            self.id = secrets.token_urlsafe(nbytes=4)
            used_artifact = f'{self.id}.json' in os.listdir('artifacts')
        
        self.token = secrets.token_urlsafe(nbytes=16)

        self.name = name
        self.content = content

        self.created_at = int(datetime.datetime.now().timestamp())
        self.modified_at = int(datetime.datetime.now().timestamp())
    
    def to_dict(self, fields: list[str]=fields):
        output = {}

        for f in fields:
            output[f] = self.__dict__[f]
        
        return output
    
    async def save(self):
        global artifact_dict

        artifact_buffer[self.id] = self

        async def save_to_file():
            with open(f'artifacts/{self.id}.json', 'w') as f:
                json.dump(self.to_dict(), f)
            
            if artifact_dict is None:
                await Artifact.get_artifacts()

            artifact_dict[self.id] = self.to_dict(['id', 'token', 'name', 'created_at', 'modified_at'])

            async with artifact_dict_lock:
                with open('artifacts/_artifact_dict.json', 'w') as f:
                    json.dump(artifact_dict, f)

        await save_to_file()
    
    @classmethod
    def load(cls, id: str):
        if id in artifact_buffer:
            return artifact_buffer[id]
        else:
            with open(f'artifacts/{id}.json', 'r') as f:
                json_data = json.load(f)
            
            a = cls(json_data['name'], json_data['content'])

            for f in fields:
                a.__dict__[f] = json_data[f]
            
            artifact_buffer[a.id] = a
            return a
    
    @classmethod
    async def get_artifacts(cls):
        global artifact_dict

        if artifact_dict is None:
            if '_artifact_dict.json' in os.listdir('artifacts'):
                async with artifact_dict_lock:
                    with open('artifacts/_artifact_dict.json') as f:
                        artifact_dict = json.load(f)
            else:
                artifact_dict = {}
        
        return artifact_dict
