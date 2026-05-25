import duckdb

from langchain_openai import AzureChatOpenAI

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    PARQUET_FILE_PATH
)

from app.tools.sql_validator import (
    validate_sql
)


# =========================================================
# INITIALIZE LLM
# =========================================================

llm = AzureChatOpenAI(

    api_key=AZURE_OPENAI_API_KEY,

    azure_endpoint=AZURE_OPENAI_ENDPOINT,

    azure_deployment=AZURE_OPENAI_DEPLOYMENT,

    api_version=AZURE_OPENAI_API_VERSION,

    temperature=0
)


# =========================================================
# DATASET SCHEMA
# =========================================================

SCHEMA = """
Table Name: sales

Columns:
- Order_ID
- Order_Date
- Ship_Date
- Ship_Mode
- Customer_ID
- Customer_Name
- Segment
- Country
- City
- State
- Region
- Product_ID
- Category
- Sub_Category
- Product_Name
- Sales
- Quantity
- Discount
- Profit
- Shipping_Days
- Profit_Margin
"""


# =========================================================
# GENERATE SQL
# =========================================================

def generate_sql(user_query: str):

    prompt = f"""
You are an expert retail analytics SQL assistant.

Your task is to convert business questions
into DuckDB SQL queries.

STRICT RULES:

1. ONLY use provided schema.
2. ONLY generate SELECT queries.
3. NEVER generate explanations.
4. NEVER generate markdown.
5. NEVER generate ```sql
6. NEVER generate text before SQL.
7. ONLY return raw SQL query.
8. ALWAYS use parquet_scan('{PARQUET_FILE_PATH}')
9. If unrelated question return:
QUESTION_NOT_RELATED_TO_DATASET

BUSINESS UNDERSTANDING RULES:

- "performing poorly"
  → lowest sales OR lowest profit

- "best performing"
  → highest sales OR highest profit

- "underperforming category"
  → category with lowest sales

- "top products"
  → highest selling products

- "worst category"
  → lowest revenue category

- "growth"
  → compare sales or profit trends

- "strongest region"
  → highest sales region

- "weakest region"
  → lowest sales region

- "improve sales"
  → identify low-performing category first

IMPORTANT:
If the user asks about:
- sales
- products
- categories
- regions
- customers
- profit
- retail performance
- business growth

Then ALWAYS generate SQL.

Schema:

{SCHEMA}

User Question:
{user_query}
"""

    response = llm.invoke(prompt)

    sql_query = response.content.strip()

    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    sql_query = sql_query.strip()

    # =====================================================
    # DEBUG
    # =====================================================

    print("\nGENERATED SQL:\n")

    print(sql_query)

    return sql_query


# =========================================================
# EXECUTE SQL
# =========================================================

def execute_sql(query: str):

    conn = duckdb.connect()

    result = conn.execute(query).fetchdf()

    conn.close()

    return result.to_dict(
        orient="records"
    )


# =========================================================
# MAIN SQL TOOL
# =========================================================

def run_sql_tool(user_query: str):

    try:

        # =================================================
        # GENERATE SQL
        # =================================================

        generated_sql = generate_sql(
            user_query
        )

        # =================================================
        # HANDLE INVALID QUESTIONS
        # =================================================

        if (
            "QUESTION_NOT_RELATED_TO_DATASET"
            in generated_sql
        ):

            return {

                "success": False,

                "error": (
                    "Question is unrelated "
                    "to retail dataset"
                )
            }

        # =================================================
        # VALIDATE SQL
        # =================================================

        is_valid, message = validate_sql(
            generated_sql
        )

        if not is_valid:

            return {

                "success": False,

                "generated_sql": generated_sql,

                "error": message
            }

        # =================================================
        # EXECUTE SQL
        # =================================================

        data = execute_sql(
            generated_sql
        )

        # =================================================
        # EMPTY RESULT HANDLING
        # =================================================

        if not data:

            return {

                "success": False,

                "generated_sql": generated_sql,

                "error": (
                    "No data found "
                    "for the query"
                )
            }

        # =================================================
        # SUCCESS
        # =================================================

        return {

            "success": True,

            "user_query": user_query,

            "generated_sql": generated_sql,

            "data": data
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }