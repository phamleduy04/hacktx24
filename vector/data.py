import openai
import json
import os
from typing import List, Dict, Any
from datasets import Dataset
import random
from tqdm import tqdm
import time
from huggingface_hub import login, HfApi
import argparse

class QADatasetGenerator:
    def __init__(self, api_key: str):
        """Initialize the dataset generator with OpenAI API."""
        self.client = openai.OpenAI(api_key=api_key)
        
        self.system_prompt = """
        You are a JSON generator. Generate JSON data in the following format:
        {
            "time": "HH:MM",
            "people": [
                {
                    "clothes": ["item1", "item2", ...]
                }
            ]
        }
        The time should be in 12-hour format. Clothes should be realistic clothing items with colors.
        Include detailed descriptions like "black hoodie", "blue jeans", "white sneakers", etc.
        """

    def generate_event_json(self) -> Dict[str, Any]:
        """Generate a single event JSON using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": "Generate a new JSON object with a random time and 2-4 people with detailed clothing descriptions."}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            json_str = response.choices[0].message.content.strip()
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0].strip()
            elif '```' in json_str:
                json_str = json_str.split('```')[1].strip()
                
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error generating event JSON: {str(e)}")
            return None

    def convert_to_natural_language(self, json_data: Dict[str, Any]) -> List[str]:
        """Convert JSON data to natural language descriptions."""
        descriptions = []
        time_str = json_data["time"]
        
        for i, person in enumerate(json_data["people"], 1):
            clothes_list = person["clothes"]
            clothes_desc = " and ".join([
                ", ".join(clothes_list[:-1]),
                clothes_list[-1]
            ] if len(clothes_list) > 1 else clothes_list)
            
            description = f"At {time_str}, a person wearing {clothes_desc} walks by."
            descriptions.append(description)
            
        return descriptions

    def generate_qa_pair(self, context: List[str], event_time: str) -> List[Dict[str, Any]]:
        """Generate question-answer pairs for the given context."""
        try:
            context_text = " ".join(context)
            
            # Generate QA pairs using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Generate a natural question and answer pair about the people described in the context. The question should be about their appearance or timing, and the answer should be a complete sentence."},
                    {"role": "user", "content": f"Context: {context_text}\nGenerate 2 different question-answer pairs about who appeared and what they were wearing."}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            qa_pairs = []
            
            # Time-based question
            qa_pairs.append({
                "context": context,
                "question": f"Who appeared around {event_time}?",
                "answer": context[0].replace(f"At {event_time}, ", "")
            })
            
            # Clothing-based question
            if len(context) > 1:
                qa_pairs.append({
                    "context": context,
                    "question": "How many people were observed and what were they wearing?",
                    "answer": f"There were {len(context)} people observed: {' '.join(context)}".replace(f"At {event_time}, ", "")
                })
            
            return qa_pairs
            
        except Exception as e:
            print(f"Error generating QA pairs: {str(e)}")
            return []

    def generate_dataset(self, num_samples: int) -> Dataset:
        """Generate a complete dataset with the specified number of samples."""
        all_qa_pairs = []
        
        for _ in tqdm(range(num_samples), desc="Generating samples"):
            event_json = self.generate_event_json()
            if not event_json:
                continue
                
            context = self.convert_to_natural_language(event_json)
            qa_pairs = self.generate_qa_pair(context, event_json["time"])
            all_qa_pairs.extend(qa_pairs)
            
            time.sleep(1)  # Rate limiting
        
        dataset_dict = {
            "context": [],
            "question": [],
            "answer": []
        }
        
        for qa_pair in all_qa_pairs:
            dataset_dict["context"].append(qa_pair["context"])
            dataset_dict["question"].append(qa_pair["question"])
            dataset_dict["answer"].append(qa_pair["answer"])
        
        return Dataset.from_dict(dataset_dict)

def push_to_hub(dataset: Dataset, repo_name: str, token: str):
    """Push the dataset to Hugging Face Hub."""
    try:
        # Login to Hugging Face
        login(token=token)
        
        # Create dataset card
        dataset_card = f"""
---
language:
- en
tags:
- surveillance
- question-answering
- temporal-qa
license: mit
---

# Surveillance QA Dataset

This dataset contains question-answer pairs about people's appearances and timings in surveillance-like scenarios.

## Dataset Structure

- context: List of descriptions about people and their appearances at specific times
- question: Questions about timing and appearance of people
- answer: Semantic answers based on the context

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{repo_name}")
```

## Examples

{json.dumps(dataset[:2], indent=2)}
"""

        # Push to hub
        dataset.push_to_hub(
            repo_name,
            private=False,
            token=token,
            # readme_content=dataset_card
        )
        
        print(f"\nDataset successfully pushed to: https://huggingface.co/datasets/{repo_name}")
        
    except Exception as e:
        print(f"Error pushing to hub: {str(e)}")

def main():
    """Main function to generate and upload the dataset."""
    parser = argparse.ArgumentParser(description='Generate and upload QA dataset to Hugging Face Hub')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples to generate')
    parser.add_argument('--repo-name', type=str, required=True, help='Repository name for Hugging Face Hub')
    args = parser.parse_args()

    # Get required environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    if not hf_token:
        print("Error: HUGGINGFACE_TOKEN environment variable not set")
        return

    # Initialize generator
    generator = QADatasetGenerator(api_key)
    
    # Generate dataset
    print(f"\nGenerating dataset with {args.samples} samples...")
    dataset = generator.generate_dataset(args.samples)
    
    # Print sample
    print("\nSample from generated dataset:")
    print(dataset[:2])
    
    # Push to Hub
    print("\nPushing dataset to Hugging Face Hub...")
    push_to_hub(dataset, args.repo_name, hf_token)

if __name__ == "__main__":
    main()