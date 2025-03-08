from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
import re  # Importing regex module for sanitizing bold tags and markdown

# Load environment variables
load_dotenv()

app = Flask(__name__)

# DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Full default resume experience (your base experience)
DEFAULT_EXPERIENCE = """
DIVINITY SCIENCE AUSTIN, TX
Data Analyst 07/2024 – Present
• Conducted data management and quality control, processing over 10,000+ feedback entries to ensure accuracy and consistency for
actionable insights.
• Integrated OpenAI’s GPT-4 API to automate advanced natural language processing (NLP) tasks, including summarization and
sentiment analysis, enhancing qualitative data workflows.
• Performed exploratory data analysis (EDA) and statistical analysis using Python (pandas, numpy) to identify trends and insights relevant
to sustainability and operational efficiency. Designed and delivered 5 interactive Power BI dashboards, incorporating dynamic
visualizations to present performance metrics, trends, and actionable insights.
• Leveraged SQL (window functions: rank(), row_number(), lead(), lag()) for data preparation, manipulation, and validation tasks.
• Presented key performance indicators (KPIs), market trends, and customer insights to stakeholders, including C-level executives, guiding
strategic decisions.
• Applied advanced text analysis techniques to streamline qualitative data processing, enabling proactive identification of retention strategies
and operational bottlenecks.
UNIVERSITY OF TEXAS AT ARLINGTON ARLINGTON, TX
Data Assistant 02/2024 - 05/2024
• Organized and cleaned datasets in Excel while ensuring data integrity through quality checks. Supported the creation of Tableau
visualizations, enabling departmental decision-making by presenting clear insights from diverse data sources.
• Coordinated the collection and preparation of data for reports, contributing to improved project tracking and operational efficiency.
Maintained student information systems with strict adherence to institutional policies on data confidentiality.
SAGE THERAPEUTICS BOSTON, MA
Data Analyst 05/2023 - 08/2023
• Developed a sentiment analysis model using the Lasso-Lars algorithm with an 87% accuracy rate; evaluated performance using metrics
like MSE, RMSE, and MAE (sklearn).
• Automated workflows by implementing 4 AI use cases in Dataiku DSS, increasing efficiency by 30%. Conducted EDA using Python
(pandas, matplotlib) and created interactive dashboards in Power BI for decision-making.
• Processed weekly KPIs with Python and SQL (MySQL), maintained ETL pipelines, and documented workflows in JIRA under SCRUM
(Agile). Used Git for code versioning.
• Validated data accuracy in Dataiku ML Flow; identified pipeline weaknesses and provided ad-hoc Python-based analytical support to
streamline workflows.
TECHNOSOFT SOLUTIONS HYDERABAD, INDIA
Marketing Data Analyst 06/2020 - 07/2022
• Analyzed data and built reports with Excel and Tableau, leading to a 35% improvement in engagement scores. Leveraged AWS to
integrate, analyze, and visualize large datasets, enhancing data processing efficiency through data exploration, data wrangling, and feature
engineering.
• Conducted validation, reviewing, cleaning, and querying of data using SQL to identify data discrepancies, missing values, and anomalies.
• Managed 2 end-to-end business intelligence projects, from requirements gathering and data analysis to solution design, implementation.
• Implemented advanced data visualization techniques using Tableau and Python libraries (e.g., Matplotlib, Seaborn), creating interactive
reports that improved stakeholder understanding of complex data sets by 40% and Collaborated with Operating and Finance groups to
understand their analytical needs, translate them into technical requirements. """

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize_resume():
    # Extract job description from the form
    job_description = request.form.get('job_description')

    if not job_description:
        return "Job description is required.", 400

    # Custom prompt for DeepSeek API
    custom_prompt = f"""

Task: You are an expert in resume optimization for ATS (Applicant Tracking System) compatibility. Your task is to update the resume of Sai Akhilesh by ensuring it highlights all relevant skills, tools, and keywords from a provided job description, even if Sai does not have direct experience with them. Follow these steps:

Extract Skills and Tools: Carefully identify the key skills, tools, technologies, methodologies, and industry-specific terminology mentioned in the job description. This includes specific software, programming languages, frameworks, and any relevant processes.

Update Experience: Rewrite Sai’s work experience to incorporate the identified skills and tools. Ensure that the skills align with the job description. If Sai doesn’t have direct experience with certain technologies, frame the experience to reflect transferable knowledge or show that he has worked with similar technologies. Focus on how past roles can be reframed to match the expectations of the job.

Responsibilities & Achievements: Integrate key responsibilities and achievements from the job description into Sai’s work experience. Use action verbs and measurable results (such as percentage improvements, time saved, or revenue generated) to demonstrate the value Sai brought to previous roles and how those contributions align with the job's requirements.

ATS Optimization: Format the resume with clear section headings (e.g., "Experience," "Skills & Tools," "Education," "Certifications"), bullet points, and concise action verbs. Ensure the resume avoids complex formatting (e.g., tables, images) so that it is ATS-compatible. This ensures that it can be accurately read and processed by ATS software.

Metrics & Impact: Quantify Sai’s impact in previous roles wherever possible. For example, include specific metrics like "improved operational efficiency by 30%" or "reduced data processing time by 40%." This adds measurable results that ATS and hiring managers will recognize.

Language & Tone: Match the tone and language of the job description to ensure the resume resonates with the hiring team. Use similar phrasing and terminology, while maintaining professionalism and clarity.

Customization & Transferable Skills: Even if Sai doesn’t have direct experience with certain tools or skills listed in the job description, present his background in a way that highlights his ability to quickly adapt. Emphasize his transferable skills, and show how his experience can be applied to fill any gaps in expertise.

Objective: Tailor the resume’s objective to closely align with the job description. Ensure it reflects Sai’s passion for the role and highlights how his expertise matches the employer's needs.


"
    Job Description: {job_description}

    Resume Experience: {DEFAULT_EXPERIENCE}

    Provide only the updated full experience section of the resume.
    """

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": custom_prompt}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response_data = response.json()

        updated_experience = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Remove all <strong>, <b>, or markdown-style bold (**text**) formatting using regex
        updated_experience = re.sub(r'<\/?(strong|b)>', '', updated_experience)  # Remove HTML tags <strong> or <b>
        updated_experience = re.sub(r'\*\*(.*?)\*\*', r'\1', updated_experience)  # Remove markdown-style bold (**text**)

        if not updated_experience:
            return render_template('results.html', updated_experience="Failed to generate updated experience section.")
        
        # Render results in HTML with the updated full experience section
        return render_template('results.html', updated_experience=updated_experience)

    except Exception as e:
        return render_template('results.html', updated_experience=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
