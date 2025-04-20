import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class DebateContext:
    def __init__(self, storage_dir: str = "debate_storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_debate_file(self, debate_id: str) -> str:
        return os.path.join(self.storage_dir, f"{debate_id}.json")
    
    def create_debate(self, document_path: str, prompt: str, role: str) -> str:
        debate_id = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        debate_data = {
            "id": debate_id,
            "document_path": document_path,
            "prompt": prompt,
            "role": role,
            "rounds": [],
            "current_round": 0,
            "status": "initial",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self._get_debate_file(debate_id), 'w') as f:
            json.dump(debate_data, f, indent=2)
        
        return debate_id
    
    def get_debate(self, debate_id: str) -> Optional[Dict]:
        try:
            with open(self._get_debate_file(debate_id), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def add_round(self, debate_id: str, round_data: Dict) -> bool:
        debate = self.get_debate(debate_id)
        if not debate:
            return False
        
        round_data["timestamp"] = datetime.now().isoformat()
        debate["rounds"].append(round_data)
        debate["current_round"] = len(debate["rounds"])
        debate["last_updated"] = datetime.now().isoformat()
        
        with open(self._get_debate_file(debate_id), 'w') as f:
            json.dump(debate, f, indent=2)
        
        return True
    
    def update_status(self, debate_id: str, status: str) -> bool:
        debate = self.get_debate(debate_id)
        if not debate:
            return False
        
        debate["status"] = status
        debate["last_updated"] = datetime.now().isoformat()
        
        with open(self._get_debate_file(debate_id), 'w') as f:
            json.dump(debate, f, indent=2)
        
        return True
    
    def get_current_round(self, debate_id: str) -> Optional[Dict]:
        debate = self.get_debate(debate_id)
        if not debate or not debate["rounds"]:
            return None
        return debate["rounds"][-1]
    
    def get_all_rounds(self, debate_id: str) -> List[Dict]:
        debate = self.get_debate(debate_id)
        if not debate:
            return []
        return debate["rounds"] 