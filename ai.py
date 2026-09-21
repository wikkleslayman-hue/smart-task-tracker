import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def suggest_task_improvement(task_title, category):
    """
    Generate clear, practical subtasks for any type of task.
    """
    prompt = (
        f"You are a helpful assistant. Break down the task '{task_title}' "
        f"in category '{category}' into 6-10 short, realistic subtasks. "
        f"Make them detailed enough to require scrolling. "
        f"Format the answer as a simple bullet list with line breaks."
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}]
        )
        suggestion = response.choices[0].message.content.strip()
        return suggestion if suggestion else "No suggestion returned."
    except Exception as e:
        return f"AI error: {e}"
