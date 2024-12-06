from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def init_db_chain():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = f"sqlite:///{current_dir}/computer_specs.db"
    db = SQLDatabase.from_uri(db_path)
    
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-1106-preview",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    chain = create_sql_query_chain(llm, db)
    return chain, db

def ask_database(question: str) -> str:
    try:
        chain, db = init_db_chain()
        # Generate SQL query
        sql_query = chain.invoke({"question": question})
        # Remove any "SQLQuery:" prefix and markdown formatting
        sql_query = sql_query.replace("SQLQuery:", "").strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        # Execute the clean query
        result = db.run(sql_query)
        return result
    except Exception as e:
        return f"Error querying database: {str(e)}"

# Example query
query = "What are the 3 computers with the highest RAM capacity?"
result = ask_database(query)
print(result)




