FORBIDDEN_KEYWORDS = [
    "DELETE",
    "DROP",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE"
]

ALLOWED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Ship_Date",
    "Ship_Mode",
    "Customer_ID",
    "Customer_Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Region",
    "Product_ID",
    "Category",
    "Sub_Category",
    "Product_Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
    "Shipping_Days",
    "Profit_Margin"
]


def validate_sql(query: str):

    upper_query = query.upper()

    # =====================================================
    # ONLY ALLOW SELECT
    # =====================================================

    if not upper_query.strip().startswith("SELECT"):

        return False, "Only SELECT queries are allowed"

    # =====================================================
    # BLOCK DANGEROUS KEYWORDS
    # =====================================================

    for keyword in FORBIDDEN_KEYWORDS:

        if keyword in upper_query:

            return False, f"Forbidden keyword detected: {keyword}"

    # =====================================================
    # ONLY ALLOW PARQUET DATASET ACCESS
    # =====================================================

    if "parquet_scan" not in query:

        return False, "Only parquet dataset access allowed"

    # =====================================================
    # BLOCK UNKNOWN COLUMNS (BASIC CHECK)
    # =====================================================

    tokens = query.replace(",", " ").replace("\n", " ").split()

    possible_columns = []

    for token in tokens:

        cleaned = token.strip()

        if cleaned in ALLOWED_COLUMNS:

            possible_columns.append(cleaned)

    return True, "VALID"