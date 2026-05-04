# from pydantic import BaseModel, Field
# from typing import List
# import os
# from dotenv import load_dotenv
# # LangChain Imports
# from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser
# from langchain_anthropic import ChatAnthropic
# load_dotenv()

# class BrandRecommendation(BaseModel):
#     brand_name:str= Field(description="The name of the protein powder brand")
#     rank:int= Field(description="Ranking position (1 to 5)")
#     reasoning:str= Field(description="Brief explanation for this ranking")
# class ProteinReport(BaseModel):
#     recommendations: List[BrandRecommendation]

# gpt_model= ChatOpenAI(model="gpt-4-0613")
# # gemini_model=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# claude_model= ChatAnthropic(model_name="claude-opus-4-7")

# #parser
# parser= PydanticOutputParser(pydantic_object=ProteinReport)

# #prompt
# prompt= ChatPromptTemplate.from_messages([
#     ("system", "You are an expert nutrition product analyst. Always return JSON."), 
#     ("user", "Analyze the following query and provide a top-3 ranking: {query}\n\n{format_instructions}")
# ])

# prompt_with_instructions = prompt.partial(format_instructions=parser.get_format_instructions())

# #create chain Prompt->Model-> Parser

# gpt_chain= prompt_with_instructions | gpt_model| parser
# # gemini_chain= prompt_with_instructions | gemini_model | parser
# claude_chain= prompt_with_instructions| claude_model| parser

# #run diagnostic
# def run_aeo_diagnostic(query_text):
#     print(f"Analyzing: {query_text}...")

#     #fetch results
#     gpt_results = gpt_chain.invoke({"query": query_text})
#     # gemini_results = gemini_chain.invoke({"query": query_text})
#     claude_results= claude_chain.invoke({"query": query_text})

#     return {
#         "GPT": gpt_results, 
#         # "Gemini": gemini_results, 
#         "Claude": claude_results
#     }

# if __name__=="__main__":
#     query = "Best whey protein isolate for lactose intolerant athletes"
#     final_report = run_aeo_diagnostic(query)

#     for model_name, report in final_report.items():
#         print(f"{model_name} Rankings----")
#         for rec in report.recommendations:
#             print(f"{rec.rank}. {rec.brand_name}: {rec.reasoning}")