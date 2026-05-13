
CREATE TABLE orders (
    row_id INT PRIMARY KEY,
    order_id VARCHAR(25),
    order_date DATE,
    segment VARCHAR(50),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(4,2),
    profit DECIMAL(10,2)
);
COPY orders FROM '/Users/shreyd04/SuperStore Sales Dashboard/data/samplesuperstore.csv' 
WITH (FORMAT csv, HEADER true, ENCODING 'windows-1252');