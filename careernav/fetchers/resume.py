from typing import List

def parse_resume(pdf_path: str) -> List[str]:
    """
    Mock implementation since we use GPT-4o Vision.
    Fakes parser extraction based on filename metadata.
    """
    filename = pdf_path.lower()
    if "lazy" in filename: 
        return ["HTML", "CSS"]
    if "overachiever" in filename: 
        return ["HTML", "CSS", "JavaScript", "React", "Python", "Machine Learning"]
    if "switcher" in filename: 
        return ["Python"]
    if "panic" in filename: 
        return ["Java", "C++"] # Out of our 19 nodes but realistic edge-case
    return ["HTML"]
