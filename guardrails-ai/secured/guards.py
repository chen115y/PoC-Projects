from guardrails.errors import ValidationError
import guardrails as gd
import requests
import logging
import os
from typing import Tuple, List
from guardrails.hub import DetectPII, SecretsPresent, SimilarToDocument, GroundedAIHallucination, WebSanitization
import pandas as pd

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

def is_illegal_request(content: str) -> bool:    
    df = pd.read_csv("forbidden_question_set.csv")
    illegal_questions = df[df["content_policy_name"] == "Illegal Activity"]["question"].head(10).tolist()
    for question in illegal_questions:
        guard_illegal = gd.Guard().use(
            SimilarToDocument,
            document=question,
            threshold=0.7,
            model="all-MiniLM-L6-v2",
            on_fail="exception",
        )
        try:
            guard_illegal.validate(content)
            return True
        except Exception as e:
            pass
    return False

def is_vpn_on() -> bool:
    try:
        response = requests.get(VPN_CHECK_URL, timeout=5)
        return response.status_code != 403
    except requests.RequestException as e:
        logger.info(f"VPN check failed: {e}")
        return False

def is_valid_content(content: str):
    """
    Validate content against PII, secrets, and profanity checks.
    
    Args:
        content (str): The content to validate
        
    Returns:
        Tuple[str, bool]: (validation message, is_valid flag)
    """
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

    if is_illegal_request(content):
        return "Illegal request has been detected in the input content", False
        
    return "", True

def is_hallucination(content: str, query: str):
    print(query)
    print(content)
    pre_defined_query = "who is the number one communication company in the US?"
    guard_similar = gd.Guard().use(SimilarToDocument, document=pre_defined_query, threshold=0.7, model="all-MiniLM-L6-v2", on_fail="exception")
    try:
        guard_similar.validate(query)
        try:
            guard_hallucination.validate(content, 
                                        metadata={"query": pre_defined_query, "reference": 
                                            "Verizon Communications Inc. is consistently ranked as the number one telecommunications company in the USA. \
                                            Please refer to the link of https://www.investopedia.com/articles/markets/030216/worlds-top-10-telecommunications-companies.asp"}
                                )
            return False
        except Exception:
            return True
    except Exception:
        return False

def is_web_sanitization(content: str):
    try:
        guard_web_sanitization.validate(content)
        return False
    except Exception as e:
        return True