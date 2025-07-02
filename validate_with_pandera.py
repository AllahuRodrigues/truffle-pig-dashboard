import pandas as pd
import pandera as pa
from pandera.errors import SchemaError

# --- 1. Define the Schema for Order-Line Data (Task 8.1 & 2) ---
# This schema enforces data types and validation rules as per the brief.
order_schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(str, nullable=False),
        "customer_id": pa.Column(str, nullable=False),
        "order_datetime": pa.Column(pa.DateTime, coerce=True),
        "sku": pa.Column(str),
        "qty": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(1)),
        "unit_price": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0.0)),
        "discount": pa.Column(float)
    },
    # Ensure no extra columns are present
    strict=True,
    # Ensure columns appear in this order
    ordered=True
)


# --- 2. Create Sample Data for Testing ---
# This data includes one good row and two bad rows to test the validation.
sample_data = {
    'order_id': ['1001', '1002', '1003'],
    'customer_id': ['cust_a', 'cust_b', None], # Bad row: null customer_id
    'order_datetime': ['2025-07-02 10:00', '2025-07-02 11:00', '2025-07-02 12:00'],
    'sku': ['SKU01', 'SKU02', 'SKU03'],
    'qty': [2, 0, 5], # Bad row: qty < 1
    'unit_price': [10.0, 15.0, 20.0],
    'discount': [0.1, 0.0, 0.2]
}
sample_df = pd.DataFrame(sample_data)


# --- 3. Run the Validation ---
if __name__ == "__main__":
    print("--- Running Pandera Schema Validation ---")
    try:
        # The validate() method will check the DataFrame against the schema.
        # If it fails, it will raise a SchemaError.
        validated_df = order_schema.validate(sample_df, lazy=True)
        print("\nValidation Successful! DataFrame conforms to the schema.")
        print(validated_df)
    except SchemaError as err:
        print("\nSchema Validation Failed!")
        # The error object contains detailed information about the failures.
        print("\nFailure Cases DataFrame:")
        print(err.failure_cases)
        # The original data that caused the error
        print("\nOriginal Data that Failed:")
        print(err.data)