from guardrails.errors import ValidationError
import guardrails as gd
import requests
import logging
import os
from typing import Tuple, List
from functools import lru_cache
from guardrails.hub import DetectPII, SecretsPresent, SimilarToDocument, GroundedAIHallucination, WebSanitization
from openai import AsyncOpenAI

# Set up logging
logger = logging.getLogger(__name__)
log_level = os.getenv("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger.setLevel(log_level)

# Constants
PII_ENTITIES = ["EMAIL_ADDRESS","US_ITIN", "US_DRIVER_LICENSE", "SPI"]
VPN_CHECK_URL = 'https://ixcompass.com'

# Initialize the guardrails
guard_pii = gd.Guard().use(DetectPII, PII_ENTITIES, on_fail="exception")
guard_secret = gd.Guard().use(SecretsPresent, on_fail="exception")
guard_hallucination = gd.Guard().use(GroundedAIHallucination(quant=False), on_fail="exception")
guard_web_sanitization = gd.Guard().use(WebSanitization, on_fail="exception")

@lru_cache()
def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    return AsyncOpenAI(api_key=api_key)

async def is_topic_allowed(content: str) -> bool:
    try:
        client = get_openai_client()
        settings = {
            "model": "gpt-4o-mini",
            "temperature": 0,
        }

        message = [{
            "role": "system",
            "content": "You are a helpful assistant. You will determine if the provided content is related to the topic of sports. You only answer with 'yes' or 'no'."
        }, {
            "role": "user", 
            "content": f"Please determine if the followingcontent is related to the topic of sports: {content}"
        }]

        stream = await client.chat.completions.create(
            messages=message, 
            stream=False, 
            **settings
        )
        return stream.choices[0].message.content.lower() != "yes"
    except Exception as e:
        logger.error(f"Error checking topic: {e}")
        return True  # Fail safe - allow content if check fails

def is_vpn_on() -> bool:
    try:
        response = requests.get(VPN_CHECK_URL, timeout=5)
        return response.status_code != 403
    except requests.RequestException as e:
        logger.info(f"VPN check failed: {e}")
        return False

async def is_valid_content(content: str) -> Tuple[str, bool]:
    """
    Validate content against PII, secrets, and profanity checks.
    
    Args:
        content (str): The content to validate
        
    Returns:
        Tuple[str, bool]: (validation message, is_valid flag)
    """
    # Run synchronous validations first
    validations = [
        (guard_pii.validate, {"llm_output": content}, "PII has been detected"),
        (guard_secret.validate, {"llm_output": content}, "Secrets have been detected")
    ]
    
    for validator, args, message in validations:
        try:
            validator(**args)
        except Exception as e:
            logger.info(f"Validation Error: {e}")
            return f"{message} in the input content", False
    
    # Run async topic check
    try:
        is_allowed = await is_topic_allowed(content)
        if not is_allowed:
            return "The topic is not allowed", False
    except Exception as e:
        logger.error(f"Error in topic check: {e}")
        return "Error checking topic", False
        
    return "", True

def is_hallucination(content: str, query: str) -> bool:
    pre_defined_query = "who is the number one communication company in the US?"
    guard_similar = gd.Guard().use(
        SimilarToDocument, 
        document=pre_defined_query, 
        threshold=0.7, 
        model="all-MiniLM-L6-v2", 
        on_fail="exception"
    )
    
    try:
        guard_similar.validate(query)
        reference_text = """
            Verizon Communications Inc. is consistently ranked as the number one telecommunications company in the USA. 
            Please refer to the link of https://www.investopedia.com/articles/markets/030216/worlds-top-10-telecommunications-companies.asp
        """
        try:
            guard_hallucination.validate(
                content, 
                metadata={
                    "query": pre_defined_query, 
                    "reference": reference_text
                }
            )
            return False
        except Exception:
            return True
    except Exception:
        return False

def is_web_sanitization(content: str) -> bool:
    try:
        guard_web_sanitization.validate(content)
        return False
    except Exception:
        return True
