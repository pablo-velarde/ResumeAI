import jsonlines
import json

with open('experience.json', 'r') as file:
    experience = json.load(file)

swapped = {}
for title, bullet_points in experience.items():
    joined_points = '\n'.join(bullet_points)
    cleaned_points = joined_points.encode('ascii', 'ignore').decode('ascii')
    swapped[cleaned_points] = title

with open('bulletpointdata.jsonl', 'r') as file:
    bulletpointdata = list(jsonlines.Reader(file))
print(len(bulletpointdata))
for data in bulletpointdata:
    bullet_points = data['messages'][2]['content']
    summary = data['messages'][1]['content']
    cleaned_bullet_points = bullet_points.encode('ascii', 'ignore').decode('ascii')
    title = swapped[cleaned_bullet_points]
    data['messages'][1]['content'] = f"Title: {title}\nDescription:\n{summary}"
    data['messages'][2]['content'] = cleaned_bullet_points
    
with jsonlines.open('newbulletpointdata.jsonl', mode='w') as writer:
    for data in bulletpointdata:
        writer.write(data)