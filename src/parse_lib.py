import json
import re
from pathlib import Path
from typing import IO

import openai
import pdftotext
import tiktoken
from fastapi import UploadFile

from src.config import logger

# based on the design by: https://github.com/hxu296/nlp-resume-parser/


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class ResumeParser:
    def __init__(self, OPENAI_API_KEY):
        openai.api_key = OPENAI_API_KEY

        self.prompt_questions = "Summarize the text below into a JSON with "
        "exactly the following structure {basic_info: {first_name, last_name, "
        "full_name, email, phone_number, location, portfolio_website_url, "
        "linkedin_url, github_main_page_url, university, education_level (BS, MS, or PhD), "
        "graduation_year, graduation_month, majors, GPA}, work_experience: [{job_title, company, "
        "location, duration, job_summary}], project_experience:[{project_name, project_description}]}"

    def pdf2string(self: object, pdf_file: IO) -> str:
        pdf = pdftotext.PDF(pdf_file)

        pdf_str = "\n\n".join(pdf)
        pdf_str = re.sub(r'\s[,.]', ',', pdf_str)
        pdf_str = re.sub(r'[\n]+', '\n', pdf_str)
        pdf_str = re.sub(r'[\s]+', ' ', pdf_str)
        pdf_str = re.sub(r'http[s]?(://)?', '', pdf_str)

        return pdf_str

    def query_completion(
        self,
        prompt: str,
        engine: str = 'text-curie-001',
        temperature: float = 0.0,
        max_tokens: int = 100,
        top_p: int = 1,
        frequency_penalty: int = 0,
        presence_penalty: int = 0,
    ) -> object:
        logger.info(f'query_completion: using {engine}')

        estimated_prompt_tokens = num_tokens_from_string(prompt, engine)
        estimated_answer_tokens = max_tokens - estimated_prompt_tokens
        logger.info(f'Tokens: {estimated_prompt_tokens} + {estimated_answer_tokens} = {max_tokens}')

        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=estimated_answer_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        return response

    def query_resume(self: object, pdf_file: UploadFile | Path) -> dict:
        resume = {}
        if isinstance(pdf_file, Path):
            with open(pdf_file, 'rb') as fp:
                pdf_str = self.pdf2string(fp)
        else:
            pdf_str = self.pdf2string(pdf_file)

        prompt = self.prompt_questions + '\n' + pdf_str

        # Reference: https://platform.openai.com/docs/models/gpt-3-5
        engine = 'text-davinci-002'
        max_tokens = 4097

        response = self.query_completion(prompt, engine=engine, max_tokens=max_tokens)
        response_text = response['choices'][0]['text'].strip()
        resume = json.loads(response_text)
        return resume
