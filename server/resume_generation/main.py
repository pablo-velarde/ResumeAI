from helpers import Conversation, classify, BulletPoints, ResumeSections,yes_or_no,cli_choice,generate_resume_pdf
from vars import finetuned


name = input("Please enter your name: ")
personal_info = ''
while True:
    personal = input('Please enter the next piece of personal information you would like to add to your resume. Type "done" when finished.')
    if personal == 'done':
        break
    else:
        personal_info += f" | {personal}"
personal_info = personal_info[3:]

## Classifying the field and position

field = classify('professional field', input('Please input the field you are applying in: '))
position = classify('job position', input("Please list the job position you are applying for: "))

## Recommending sections

section_builder = Conversation("You are an expert in identifying the best sections to include on a resume. Given a professional field and a job position, please give the 5 best sections (excluding contact information) to include on a resume.")
section_builder.add_message('user', f'professional field: {field}, job position: {position}')
section_builder.respond(output_type=ResumeSections)
sections = section_builder.messages()[-1]['content'].sections

print(f"I suggest using the sections {', '.join(sections)} on your resume.")

## Allowing user to update sections

while True:
    instructions = input("Would you like to add or remove any sections? Type 'add' or 'remove' followed by the section name, or type 'done' to continue.")
    first_word = instructions.split()[0]
    if not first_word in {'add', 'remove', 'done'}:
        print("Please type 'add', 'remove', or 'done'.")
        continue
    else:
        if first_word == 'done':
            break
        else:
            section = ' '.join(instructions.split()[1:])
            if first_word == 'add':
                sections.append(section)
                print(f"Added {section}.")
            else:
                if section not in sections:
                    print(f"{section} is not in the list of sections.")
                    continue
                else:
                    sections.remove(section)
                    print(f"Removed {section}.")

## Generating content for each section

print("Now let's generate some bullet points for each section.")

resume = []

for section in sections:
    print("Generating content for ", section)
    section_content = []
    subsections = yes_or_no('Would you like to add subsections to this section? Type "yes" or "no".')
    if subsections:
        while True:
            title = input("Provide a title for the current subsection. Type 'done' when finished.")
            if title == 'done':
                break
            bp = yes_or_no("Would you like to add bullet points to this section? Type 'yes' or 'no'.")
            if bp:
                generator = yes_or_no("Would you like to have AI generate the content for this section? Type 'yes' or 'no'.")
                if generator:
                    description = input(f"Provide a description for {title}: ")
                    num_bp = int(cli_choice("How many bullet points would you like to generate for this section? Enter a number between 1 and 4", ('1','2', '3', '4')))
                    section_builder = Conversation(f"You are an expert in creating resume bullet points from a job description. Given a job title and description, return a list of {num_bp} bullet points that describe the responsibilities and qualifications for the role.")
                    section_builder.add_message('user', f"Title: {title}\nDescription: {description}")
                    section_builder.respond(output_type=BulletPoints, model=finetuned)
                    subsection_content = section_builder.messages()[-1]['content'].bullet_points
                else:
                    subsection_content = []
                    while True:
                        point = input("Provide a bullet point for the current section. Type 'done' when finished.")
                        if point == 'done':
                            break
                        else:
                            subsection_content.append(point)
            else:
                subsection_content = input("Provide the content for this subsection.")
            section_content.append([title, subsection_content])
    else:
        section_content.append(input("Provide the content for this section."))
    resume.append([section, section_content])
print(name)
print(personal_info)
print(resume)
generate_resume_pdf(name, personal_info, resume, f"{name}_resume.pdf")
            
        

