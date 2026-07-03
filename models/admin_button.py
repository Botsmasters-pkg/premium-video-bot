from typing import Optional


class AdminButton:
    """Admin custom button model"""
    
    def __init__(self, button_id: str, label: str, button_type: str = "url"):
        self.button_id = button_id
        self.label = label
        self.button_type = button_type  # url, callback, etc.
        self.value = ""  # URL or callback data
        self.is_active = True
        self.order = 0
    
    def to_dict(self) -> dict:
        """Convert button to dictionary"""
        return {
            "button_id": self.button_id,
            "label": self.label,
            "button_type": self.button_type,
            "value": self.value,
            "is_active": self.is_active,
            "order": self.order
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'AdminButton':
        """Create button from dictionary"""
        button = AdminButton(data['button_id'], data['label'], data.get('button_type', 'url'))
        button.value = data.get('value', '')
        button.is_active = data.get('is_active', True)
        button.order = data.get('order', 0)
        return button
