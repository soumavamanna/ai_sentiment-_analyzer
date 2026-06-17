import re

def extract_company_context(text, company_name, window=2):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    matches = []

    for idx, sentence in enumerate(sentences):
        if company_name.lower() in sentence.lower():

            start = max(0, idx - window)
            end = min(len(sentences), idx + window + 1)

            matches.append(
                " ".join(sentences[start:end])
            )

    return " ".join(matches) if matches else text