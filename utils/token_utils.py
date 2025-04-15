# utils/token_utils.py

import tiktoken

def count_tokens(text, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def compute_tokens_for_stage(system_msg, user_msg, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    return {
        "system": len(encoding.encode(system_msg)),
        "user": len(encoding.encode(user_msg))
    }
