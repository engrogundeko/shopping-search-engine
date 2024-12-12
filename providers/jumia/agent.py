import os
from typing import List
from dataclasses import dataclass

from schema import PriceDetailSchema

import httpx
from dotenv import load_dotenv
from .prompt import rerank_prompt
from pydantic_ai import Agent
load_dotenv()


@dataclass
class MyDeps:  
    http_client: httpx.AsyncClient
    api_key: str = os.getenv("GROQ_API_KEY")

@dataclass
class JumiaResponse:
    name: str
    category: str

@dataclass
class Response:
    response: List[JumiaResponse]

async def rank_search_results(search_results,rank_list, search_query) -> List[PriceDetailSchema]:
    re_ranked_results = []
    try:
        system_prompt = rerank_prompt(rank_list)
        re_rank_agent = Agent(
            retries=3,
            system_prompt=system_prompt,
            model="groq:llama3-groq-70b-8192-tool-use-preview",
            result_type=Response,
            deps_type=MyDeps
            
        )
        results = await re_rank_agent.run(search_query)
        for search in search_results:
            d = search.__dict__
            for r in results.data.__dict__["response"]:
                e = r.__dict__
                if d["name"] == e["name"]:
                    re_ranked_results.append(search)

        return re_ranked_results
    except Exception as e:
        print(f"Error occurred: {e}")
    return re_ranked_results

