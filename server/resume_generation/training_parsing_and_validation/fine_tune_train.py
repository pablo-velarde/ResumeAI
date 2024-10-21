from vars import client


created_file = client.files.create(
    file=open("newbulletpointdata.jsonl", "rb"),
    purpose="fine-tune"
)

file_name = created_file.id

print(f"Successfully created file {file_name}")

client.fine_tuning.jobs.create(
  training_file=file_name, 
  model="gpt-4o-mini-2024-07-18"
)