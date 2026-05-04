from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from models import ProteinReport

load_dotenv()

gpt_model = ChatOpenAI(model="gpt-4o")
# gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
claude_model = ChatAnthropic(model_name="claude-opus-4-7")

parser = PydanticOutputParser(pydantic_object=ProteinReport)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert nutrition product analyst. Always return JSON."),
    ("user", "Analyze the following query and provide a top-3 ranking: {query}\n\n{format_instructions}")
])

prompt_with_instructions = prompt.partial(format_instructions=parser.get_format_instructions())

gpt_chain = prompt_with_instructions | gpt_model | parser
# gemini_chain = prompt_with_instructions | gemini_model | parser
claude_chain = prompt_with_instructions | claude_model | parser

ALL_CHAINS = {
    "GPT": gpt_chain,
    # "Gemini": gemini_chain,
    "Claude": claude_chain,
}