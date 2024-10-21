from dotenv import load_dotenv
import os
from openai import OpenAI
import re

load_dotenv()
openai_key = os.getenv('openai')

finetuned = 'ft:gpt-4o-mini-2024-07-18:personal::9wWNwM4P'
standard = 'gpt-4o-mini'

client = OpenAI(api_key=openai_key)
 
with open("training_parsing_and_validation/Times-Roman.afm", 'r') as afm_file:
    char_widths = {}
    for line in afm_file:
        match = re.match(r'C\s+(\d+)\s+;.*WX\s+(\d+)\s+;.*N\s+(\S+)\s+;', line)
        if match:
            code, width, _ = match.groups()
            char_widths[chr(int(code))] = int(width)
