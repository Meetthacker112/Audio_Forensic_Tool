"""
Person Management Module - Manage persons of interest for forensic audio analysis cases
"""

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PersonManager:
    """Manages persons of interest (suspects, witnesses, victims) for forensic cases"""
    
    def __init__(self, data_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), 'data', 'persons.json')
        
        self.data_path = Path(data_path)
        self.persons: List[Dict] = []
        self.load_persons()
    
    def load_persons(self) -> None:
        """Load persons from JSON file"""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.persons = data.get('persons', [])
                self.logger.info(f"Loaded {len(self.persons)} persons from {self.data_path}")
            else:
                self.persons = []
                self.save_persons()
                self.logger.info(f"Created new persons file at {self.data_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing persons file: {e}")
            self.persons = []
        except Exception as e:
            self.logger.error(f"Error loading persons: {e}")
            self.persons = []
    
    def save_persons(self) -> bool:
        """Save persons to JSON file"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({'persons': self.persons}, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.persons)} persons to {self.data_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving persons: {e}")
            return False
    
    def add_person(self, name: str, role: str = "Unknown", 
                   description: str = "", notes: str = "",
                   contact: str = "", case_ids: List[str] = None) -> Optional[Dict]:
        """
        Add a new person to the database
        
        Args:
            name: Person's name (required)
            role: Person's role (Suspect, Witness, Victim, Person of Interest, Other)
            description: Physical or identifying description
            notes: Additional notes about the person
            contact: Contact information if available
            case_ids: List of associated case/analysis IDs
        
        Returns:
            The created person dict, or None if creation failed
        """
        if not name or not name.strip():
            self.logger.error("Cannot add person without a name")
            return None
        
        person = {
            'id': str(uuid.uuid4()),
            'name': name.strip(),
            'role': role,
            'description': description,
            'notes': notes,
            'contact': contact,
            'case_ids': case_ids or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.persons.append(person)
        
        if self.save_persons():
            self.logger.info(f"Added person: {name} ({role})")
            return person
        else:
            self.persons.pop()
            return None
    
    def update_person(self, person_id: str, **kwargs) -> Optional[Dict]:
        """
        Update an existing person's information
        
        Args:
            person_id: The unique ID of the person to update
            **kwargs: Fields to update (name, role, description, notes, contact, case_ids)
        
        Returns:
            The updated person dict, or None if update failed
        """
        for i, person in enumerate(self.persons):
            if person['id'] == person_id:
                allowed_fields = ['name', 'role', 'description', 'notes', 'contact', 'case_ids']
                
                for field, value in kwargs.items():
                    if field in allowed_fields:
                        self.persons[i][field] = value
                
                self.persons[i]['updated_at'] = datetime.now().isoformat()
                
                if self.save_persons():
                    self.logger.info(f"Updated person: {person_id}")
                    return self.persons[i]
                break
        
        self.logger.warning(f"Person not found: {person_id}")
        return None
    
    def delete_person(self, person_id: str) -> bool:
        """
        Delete a person from the database
        
        Args:
            person_id: The unique ID of the person to delete
        
        Returns:
            True if deletion was successful, False otherwise
        """
        for i, person in enumerate(self.persons):
            if person['id'] == person_id:
                deleted_person = self.persons.pop(i)
                
                if self.save_persons():
                    self.logger.info(f"Deleted person: {deleted_person['name']}")
                    return True
                else:
                    self.persons.insert(i, deleted_person)
                    return False
        
        self.logger.warning(f"Person not found for deletion: {person_id}")
        return False
    
    def get_person(self, person_id: str) -> Optional[Dict]:
        """
        Get a person by their ID
        
        Args:
            person_id: The unique ID of the person
        
        Returns:
            The person dict, or None if not found
        """
        for person in self.persons:
            if person['id'] == person_id:
                return person
        return None
    
    def get_all_persons(self) -> List[Dict]:
        """
        Get all persons in the database
        
        Returns:
            List of all person dicts
        """
        return self.persons.copy()
    
    def search_persons(self, query: str) -> List[Dict]:
        """
        Search persons by name or description
        
        Args:
            query: Search query string
        
        Returns:
            List of matching person dicts
        """
        if not query:
            return self.persons.copy()
        
        query_lower = query.lower()
        results = []
        
        for person in self.persons:
            if (query_lower in person.get('name', '').lower() or
                query_lower in person.get('description', '').lower() or
                query_lower in person.get('notes', '').lower() or
                query_lower in person.get('role', '').lower()):
                results.append(person)
        
        return results
    
    def get_persons_by_role(self, role: str) -> List[Dict]:
        """
        Get all persons with a specific role
        
        Args:
            role: The role to filter by
        
        Returns:
            List of person dicts with the specified role
        """
        return [p for p in self.persons if p.get('role', '').lower() == role.lower()]
    
    def get_persons_by_case(self, case_id: str) -> List[Dict]:
        """
        Get all persons associated with a specific case
        
        Args:
            case_id: The case/analysis ID to filter by
        
        Returns:
            List of person dicts associated with the case
        """
        return [p for p in self.persons if case_id in p.get('case_ids', [])]
    
    def associate_person_with_case(self, person_id: str, case_id: str) -> bool:
        """
        Associate a person with a case/analysis
        
        Args:
            person_id: The unique ID of the person
            case_id: The case/analysis ID to associate
        
        Returns:
            True if association was successful, False otherwise
        """
        for i, person in enumerate(self.persons):
            if person['id'] == person_id:
                if case_id not in person.get('case_ids', []):
                    if 'case_ids' not in self.persons[i]:
                        self.persons[i]['case_ids'] = []
                    self.persons[i]['case_ids'].append(case_id)
                    self.persons[i]['updated_at'] = datetime.now().isoformat()
                    return self.save_persons()
                return True
        return False
    
    def remove_person_from_case(self, person_id: str, case_id: str) -> bool:
        """
        Remove a person's association with a case
        
        Args:
            person_id: The unique ID of the person
            case_id: The case/analysis ID to remove
        
        Returns:
            True if removal was successful, False otherwise
        """
        for i, person in enumerate(self.persons):
            if person['id'] == person_id:
                if case_id in person.get('case_ids', []):
                    self.persons[i]['case_ids'].remove(case_id)
                    self.persons[i]['updated_at'] = datetime.now().isoformat()
                    return self.save_persons()
                return True
        return False
    
    def get_person_count(self) -> int:
        """
        Get the total number of persons in the database
        
        Returns:
            Number of persons
        """
        return len(self.persons)
    
    def get_role_statistics(self) -> Dict[str, int]:
        """
        Get statistics about person roles
        
        Returns:
            Dict with role counts
        """
        stats = {}
        for person in self.persons:
            role = person.get('role', 'Unknown')
            stats[role] = stats.get(role, 0) + 1
        return stats
    
    def export_persons(self, output_path: str) -> bool:
        """
        Export persons to a JSON file
        
        Args:
            output_path: Path to export file
        
        Returns:
            True if export was successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'total_count': len(self.persons),
                    'persons': self.persons
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(self.persons)} persons to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting persons: {e}")
            return False
    
    def import_persons(self, input_path: str, merge: bool = True) -> int:
        """
        Import persons from a JSON file
        
        Args:
            input_path: Path to import file
            merge: If True, merge with existing persons; if False, replace all
        
        Returns:
            Number of persons imported
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_persons = data.get('persons', [])
            
            if not merge:
                self.persons = []
            
            imported_count = 0
            existing_ids = {p['id'] for p in self.persons}
            
            for person in imported_persons:
                if person.get('id') not in existing_ids:
                    if 'id' not in person:
                        person['id'] = str(uuid.uuid4())
                    self.persons.append(person)
                    imported_count += 1
            
            if self.save_persons():
                self.logger.info(f"Imported {imported_count} persons from {input_path}")
                return imported_count
            return 0
            
        except Exception as e:
            self.logger.error(f"Error importing persons: {e}")
            return 0
