from openai import OpenAI
from django.conf import settings

system_prompt = """
You are a technical knowledge expert tasked with generating comprehensive explanations for technologies, tools, standards, and technical concepts.
Assume the reader is technically literate but may not be familiar with the specific concept. Aim to be educational, objective and explanatory rather than promotional.
Structure your response as HTML using the following guide. Other sections may be improvised:

<h3>Introduction</h3>
<p>Provide a clear and concise summary of the technology or concept. State what it is, what it is for, and why it matters, in one or two paragraphs.</p>
<h3>Key Terms and Concepts</h3>
<ul>Define essential terms, acronyms, or ideas that a user must understand to fully grasp the technology. Use a bullet-point list format.</ul>
<h3>Explanation</h3>
<p>Break down the mechanics or underlying principles. Include the core ideas and how they work. This section should be longer, more technical and comprehensive.</p>
<h3>Use Cases</h3>
<p>List specific scenarios, problems, or environments where the technology is commonly used or is particularly well-suited. Real-world applications are preferred.</p>
// Other sections to consider
  // Limitations
  // Examples
  // Future prospects
  // Implementation details
  // etc.
<h3>See Also:</h3>
<p>Compare this technology to other related or competing technologies. Highlight key differences in approach, use case, maturity, performance, or philosophy.</p>
<p>Explain how the technology interacts with or fits into other systems. What does it depend on? What does it enable? Mention libraries, platforms, protocols, tools, etc.</p>
<h3>Further Reading / References</h3>
<ul> // Link recommended resources for deeper exploration, see below for suggestions. Use a bullet point format.
 <li><a _blank>Official documentation</a></li>
 <li><a _blank>Tutorials</a></li>
 <li><a _blank>Research Papers</a></li>
 <li><a _blank>High quality community article</a></li>
</ul>
"""

def request_new_entry(query: str) -> str:
   """
   Query the OpenAI API with a system prompt and a user input message.
   The model name is retrieved from Django settings (OPENAI_MODEL_NAME).
   """
   api_key = settings.OPENAI_API_KEY
   if not api_key:
      raise RuntimeError("OPENAI_API_KEY environment variable not set.")

   model_name = getattr(settings, "OPENAI_MODEL_NAME", None)
   if not model_name:
      raise RuntimeError("OPENAI_MODEL_NAME not configured in Django settings.")

   client = OpenAI(api_key=api_key)
   response = client.chat.completions.create(
      model=model_name,
      messages=[
         {"role": "system", "content": system_prompt},
         {"role": "user", "content": query}
      ]
   )
   return response.choices[0].message.content