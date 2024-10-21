from vars import client, standard, char_widths
import json
from pydantic import BaseModel
from fpdf import FPDF

class Conversation:
    def __init__(self, opening_prompt = "You are a helpful assistant."):  
        self.conversation_history = [{"role":"system", "content":opening_prompt}]

    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
    
    def respond(self, model=standard, output_type='text'):
        if isinstance(output_type, type(str)):
            print('using pydantic model')
            response = client.beta.chat.completions.parse(
                model=model,
                messages=self.conversation_history,
                response_format=output_type
            )
            out = response.choices[0].message.parsed
        else:
            print('using standard model')
            response = client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                response_format={"type": output_type}
            )
            out = response.choices[0].message.content
        self.add_message("assistant",out)
    
    def messages(self):
        return self.conversation_history

class Summary(BaseModel):
    summary: str

class BulletPoints(BaseModel):
    bullet_points: list[str]

class ResumeSections(BaseModel):
    sections: list[str]

def classify(item, input):
    main = Conversation(f"You are an expert in identifying the {item} the user is talking about in their response. Return the output as a JSON object with one entry of the form 'field': 'example_field' or 'error':'example_error' if the user is not talking about a {item}.")
    main.add_message('user', input)
    main.respond(output_type='json_object')
    out = json.loads(main.conversation_history[-1]['content'])
    if 'error' in out:
        print(out['error'])
    return list(out.values())[0]

def inch_len(text, pt):
    return sum(char_widths.get(char,0) for char in text)*pt/72000

def cli_choice(prompt:str, choices:tuple):
    while True:
        response = input(prompt)
        if response in choices:
            return response
        else:
            print(f"Please choose one of the following: {', '.join(choices)}")

def yes_or_no(prompt:str):
    return cli_choice(prompt, ('yes', 'no')) == 'yes'

def strip_non_latin(text):
    return text.encode('latin-1', errors='ignore').decode('latin-1')

def generate_resume_pdf(name, personal_info, sections, output_filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set section title, subsection title, and content fonts
    large_font_size = 16.5
    normal_font_size = 11
    
    large_break = 6
    small_break = 5
    
    pdf.set_font("Times", 'B', size=large_font_size)
    
    # Calculate the available width (total page width minus margins)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    
    # Set Y position for the line
    y_position = pdf.get_y()

    # Print the name left-aligned
    pdf.set_xy(pdf.l_margin, y_position)
    pdf.cell(0, large_break, txt=strip_non_latin(name), ln=0, align="L")

    # Set font for personal information with a smaller size
    pdf.set_font("Times", size=normal_font_size)
    
    # Calculate the Y position for better vertical alignment
    personal_info_y_position = y_position + 1.5  # Increased adjustment for better centering
    
    # Move to the right to align personal information right-aligned
    pdf.set_xy(pdf.l_margin + page_width - pdf.get_string_width(personal_info), personal_info_y_position)
    
    # Print personal information right-aligned
    pdf.cell(0, large_break, txt=strip_non_latin(personal_info), ln=1, align="R")

    for section in sections:
        pdf.ln(1)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        
        section_title = section[0]
        content = section[1]

        # Add section title
        pdf.set_font("Times", 'B', size=normal_font_size)
        
        pdf.cell(0, small_break, txt=strip_non_latin(section_title), ln=True)
        

        # Check if content is a list of subsections or plain text
        if isinstance(content, list) and isinstance(content[0], list):
            # If content is a list of subsections
            for subsection in content:
                subsection_title = subsection[0]
                subsection_content = subsection[1]

                # Add subsection title with smaller font size
                pdf.set_font("Times", 'B', size=normal_font_size)
                pdf.cell(0, small_break, txt=strip_non_latin(subsection_title), ln=True)

                # Check if subsection content is a list of bullet points or plain text
                if isinstance(subsection_content, list):
                    pdf.set_font("Times", size=normal_font_size)
                    for bullet_point in subsection_content:
                        pdf.cell(3)  # Indent bullet points
                        pdf.multi_cell(0, small_break, txt=strip_non_latin(f"- {bullet_point}"))  # Use hyphen instead of bullet point
                else:
                    # Add subsection content as plain text
                    pdf.set_font("Times", size=normal_font_size)
                    pdf.multi_cell(0, small_break, txt=strip_non_latin(subsection_content))

        elif isinstance(content, list) and isinstance(content[0], str):
            # If content is a list of bullet points
            pdf.set_font("Times", size=normal_font_size)
            for bullet_point in content:
                pdf.cell(3)  # Indent bullet points
                pdf.multi_cell(0, small_break, txt=strip_non_latin(f"- {bullet_point}"))  # Use hyphen instead of bullet point
        else:
            # Add section content as plain text
            pdf.set_font("Times", size=normal_font_size)
            pdf.multi_cell(0, small_break, txt=strip_non_latin(content))

        # Add a small line break after each section
        pdf.ln(1)

    # Output the PDF to a file
    pdf.output(output_filename)
    print(f"Resume saved as {output_filename}")

if __name__ == "__main__":
    sections = [
    ["Personal Information", "Name: John Doe\nEmail: johndoe@example.com\nPhone: (123) 456-7890"],
    ["Objective", "To obtain a software engineering position at a dynamic and innovative company."],
    ["Education", [
        ["B.S. in Computer Science", "XYZ University\nGraduation: May 2023"],
        ["High School Diploma", "ABC High School\nGraduation: June 2019"]
    ]],
    ["Work Experience", [
        ["Software Engineering Intern at ABC Corp", [
            "Developed several key features for the company's flagship product.",
            "Collaborated with cross-functional teams to deliver projects on time."
        ]],
        ["Teaching Assistant", [
            "Assisted in teaching introductory programming courses at XYZ University.",
            "Conducted lab sessions and graded assignments."
        ]]
    ]],
    ["Skills", ["Python", "Java", "C++", "HTML", "CSS", "JavaScript", "Phi Delta Theta - Treasurer, MIT Physics - TA, MIT Wellbeing Lab - Ambassador, BHS Physics - TA, BHS Student Research Club: Co-Founder, BHS Varsity Soccer, BHS Jazz Band"]],
    ["Projects", [
        ["Personal Website", "Created a portfolio website using HTML, CSS, and JavaScript."],
        ["Open Source Contribution", [
            "Contributed to an open-source project on GitHub.",
            "Implemented new features and fixed bugs."
        ]]
    ]]]
    name = "John Doe"
    personal_info = "johndoe@example.com | (123) 456-7890"
    generate_resume_pdf(name, personal_info, sections, "output_files/resume.pdf")


