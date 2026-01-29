import streamlit as st
import pickle
import numpy as np

model = pickle.load(open('churn_model.pkl', 'rb'))

st.title("🏦 Bank Customer Churn Predictor")

credit = st.number_input("Credit Score", 300, 900)
age = st.number_input("Age", 18, 100)
tenure = st.number_input("Tenure", 0, 10)
balance = st.number_input("Balance", 0.0, 300000.0)
num_products = st.number_input("Number of Products", 1, 4)
has_card = st.selectbox("Has Credit Card?", [0, 1])
is_active = st.selectbox("Is Active Member?", [0, 1])
salary = st.number_input("Estimated Salary", 0.0, 200000.0)
gender = st.selectbox("Gender", ["Male", "Female"])
geo = st.selectbox("Geography", ["France", "Germany", "Spain"])

# Convert gender & geography to numeric form as per training
gender = 1 if gender == "Male" else 0
geo_france = geo_germany = geo_spain = 0
if geo == "Germany": geo_germany = 1
elif geo == "Spain": geo_spain = 1

features = np.array([[credit, gender, age, tenure, balance, num_products,
                      has_card, is_active, salary, geo_germany, geo_spain]])


import mysql.connector
import streamlit as st

if st.button("Predict"):
    prediction = model.predict(features)

    if prediction[0] == 1:
        st.error("⚠️ Customer likely to churn.")
    else:
        st.success("✅ Customer likely to stay.")

    conn = None  
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port = 3306,
            user="root",
            password="pass123",   # <-- replace this
            database="bank"
        )

        if conn.is_connected():
            cursor = conn.cursor()

            query = """
            INSERT INTO churn_results
            (CreditScore, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, 
            IsActiveMember, EstimatedSalary, Geography, Prediction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (credit, gender, age, tenure, balance, num_products,
                    has_card, is_active, salary, geo, int(prediction[0]))

            cursor.execute(query, data)
            conn.commit()

            st.success("✅ Prediction saved to MySQL database successfully!")

    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")

    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()
