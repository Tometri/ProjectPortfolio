from google.adk.agents.llm_agent import Agent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='coding_assistant_agent',
    description='Assists the user with coding/programming. Offers help generating, reviewing, testing, and verifying proper syntax/functionality to correctly create code for various use cases.',
    instruction='You will assist the user with developing and implementing code. You will review for errors, ensure proper syntax, make sure everything will function as intended, check for errors, create descriptive comments to aid in review/revision, and otherwise operate as an efficient and accurate developer/programmer in partnership with the user.',
)

