import os
from dotenv import load_dotenv
from IPython.display import Markdown, display
from openai import OpenAI
import Website


load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

website = Website()
openai = OpenAI()



system_prompt = "You are an HR professional that analyzes the job postings of a website \
and provides a short summary, ignoring text that might be navigation related, of what skills a computer science student should \
acquire based on their current resume, specific to each of the job postings."
def user_prompt (website):
    user_prompt =     """
    this right here is my resume copied from a google document:
    

IAN ROWE
(859) 285-9529 · ian.rowe.rojas@gmail.com · www.linkedin.com/in/irowe12

EDUCATION
——————————————————————————————————————————————————————
UNIVERSITY OF KENTUCKY      (Dean’s List GPA: 4.0/4.0)    			                                 May 2027
Bachelor of Science in Computer Science with a Minor in Mathematics | Honors College Member

UNIVERSITY OF MANCHESTER      (Study Abroad)			             August 2024 - January 2025
Data Science | Introduction to AI | Machine Learning | Database Systems | Distributed Systems | Logic Modelling

SKILLS AND QUALIFICATIONS
——————————————————————————————————————————————————————
Technical skills: C++ | Python | GitHub | AWS | Azure | MVC architecture | Swift | MATLAB | Flask | Numpy

EXPERIENCE 								        GitHub | github.com/ianrowe12
——————————————————————————————————————————————————————

SWE INTERN | Microsoft, Redmond WA   					                Summer 2025 - Upcoming

Collaborate with a cross-functional pod to engage in all phases of the software engineering and product development cycle—including design, build, and quality—enhancing practical skills in software engineering, product management, and technical program management.
DATA INTERN | CARES University of Kentucky               		                   February 2025 - Present

Developing, testing, and deploying automation scripts to efficiently manage and update student data 
Programming predictive algorithms that analyze complex data to support department decision-making
AUTOMATION ENGINEERING | CARES University of Kentucky                        June 2024 - September 2024

Developed and implemented Python scripts to automate administrative tasks, reducing project completion time by 85%; significantly enhancing productivity and efficiency in the office
Engineered a C++ program for automating employee scheduling, utilizing Qt for the interface, and fine-tuning a machine learning language model with LoRA to optimize scheduling further

RESEARCH UNIVERSITY OF KENTUCKY | Computer Science Department         January 2024 - June 2024
Developed the creation of website clones of popular brands (Yelp, OpenTable, TripAdvisor) by using GitHub, Python, Javascript, Flask, Jinja, HTML, CSS & Bootstrap; project used a machine learning model to navigate online and make orders with natural language processing 

FULL-STACK APP DEVELOPMENT WITH SWIFT   				      June 2021 - August 2022
Reduced waiting time in line significantly for 280 students by programming a full-stack ordering app in Swift to place orders from students’ phones to a non-relational database 
Leveraged authentication, database, and security operations from Firebase
Increased efficiency for the cafeteria by building a website for the Cafeteria to view the orders using HTML, JavaScript, and Bootstrap


HACKATHON COMPETITIONS                						    October & November 2023
Achieved finalizing second place out of the seven teams that were participating from the University of Kentucky in IEEE Xtreme’s programming competition in Data Structures and Algorithms (October)

LEADERSHIP
——————————————————————————————————————————————————————
MICROSOFT				                                     	                    Costa Rica & Washington D.C
Azure Trainer						                             Apr 2023 - Jun 2023 & Feb 2022 - April 2022
Trained a total of 31 college and black students from Costa Rica & Washington D.C weekly in preparation for the Azure Fundamentals Exam through designing interactive presentations, leading classes, breaking down concepts, and making practice quizzes

ADDITIONAL
——————————————————————————————————————————————————————
Languages: Fluent in Spanish and English
Awards: Dean’s List University of Kentucky (present), Blacks at Microsoft Academy Golden Volunteer (2022)
Memberships: Active in National Society of Black Engineers & Society of Hispanic Professional Engineers

    The contents of this website is as follows; please provide me a short summary, of what projects or 
    skills I should work on as a computer science student to be the top 1 candidate for each of these positions. Give advice individually please \n\n
"""
    user_prompt+= website.text
    return user_prompt




def messages(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt(website)},
    ] 

# Call OpenAI
def summarize(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages(website)
    )
    return response.choices[0].message.content



def display_summary(url):
    summary = summarize(url)
    display(Markdown(summary))






