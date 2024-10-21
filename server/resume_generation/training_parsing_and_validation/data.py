import pandas as pd
import re
import json
from helpers import inch_len

data = pd.read_csv('./Resume.csv')

def extract_title(text):
    """
    Given a string of text, extract the title
    of the section by getting rid of the
    remaining html tags.
    """
    for idx, char in enumerate(text):
        if char == ">":
            result = text[idx+1:]

    return result.strip()

def extract_bullet_points(text):
    """
    Given a string of text, remove all of the
    html tags that may be present, and return
    the text that is left.
    """
    result = ""
    ignore = False
    for char in text:
        if char == "<":
            ignore = True
        elif char == ">":
            ignore = False
        elif not ignore:
            result += char
    return result.strip()

def filter_section_titles(html):
    """
    Filter the section titles from the html,
    and return them as a list of strings.
    """
    section_titles = []
    pattern = r'sectiontitle(.*?)</div>'
    matches = re.findall(pattern, html)
    for match in matches:
        section_titles.append(extract_title(match))
    return section_titles

def filter_bullet_points(html):
    """
    Filter out all of the list elements in
    a string of html, and return them as a
    list of strings
    """
    bullet_points = []
    pattern = r'<li>(.*?)</li>'
    matches = re.findall(pattern, html)
    for match in matches:
        bullet_points.append(extract_bullet_points(match))
    return bullet_points

def filter_list_of_bullets(html):
    """
    Filter out all of the unordered lists in
    a string of html, and then filter out all
    of the bullet points in each list, and
    return a list of lists where each element
    in the inner list is a bullet point and
    outer list is a group of bullet points.
    """
    list_of_bullets = []
    pattern = r'<ul>(.*?)</ul>'
    matches = re.findall(pattern, html)
    for match in matches:
        list_of_bullets.append(filter_bullet_points(match))
    return list_of_bullets

def filter_expreience(html):
    """
    Filter out the experience section from the
    html and return it as a string.
    """
    result = {}
    pattern = r'jobtitle(.*?)</span>'
    other_pattern = r'jobline(.*?)</span>'
    job_titles = re.findall(pattern, html)
    job_descriptions = re.findall(other_pattern, html)
    if len(job_titles) == len(job_descriptions):
        for title_html, bullet_html in zip(job_titles, job_descriptions):
            title = extract_title(title_html)
            bullet_points = filter_bullet_points(bullet_html)
            result[title] = bullet_points
    return result

data['Experience'] = data['Resume_html'].apply(filter_expreience)

experience = {}


for resume in data['Experience']:
    if resume:
        for title, bullet_points in resume.items():
            if 2 <= len(bullet_points) <=4 and all(4.5 < inch_len(point, 10) < 6.2 for point in bullet_points):
                experience[title] = bullet_points
        if len(experience) > 200:
                break
print(len(experience))

# Save experience as a JSON file
with open('experience.json', 'w') as f:
    json.dump(experience, f)
if __name__ == "__main__":
    # # Apply the functions to the html data and create new columns
    # data['Section_Titles'] = data['Resume_html'].apply(filter_section_titles)
    # data['Bullet_Points'] = data['Resume_html'].apply(filter_bullet_points)
    # data['Best_Bullet'] = data['Bullet_Points'].apply(lambda x: max(x, key=len) if x else None)
    # data['List_of_Bullets'] = data['Resume_html'].apply(filter_list_of_bullets)
    # data['Experience'] = data['Resume_html'].apply(filter_expreience)

    # # Print the first 5 rows of the new columns
    # print(data['Section_Titles'].head())
    # print(data['Bullet_Points'].head())
    # print(data['Best_Bullet'].head())
    # print(data['List_of_Bullets'].head())
    # print(data['Experience'].head())

    # print(data.iloc[0]['Resume_html'])
    ...
