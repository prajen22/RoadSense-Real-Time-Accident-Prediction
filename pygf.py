import streamlit as st
import subprocess

def main():
    st.title("Road Safety Project")

    # Button to run the data generation script
    if st.button("Start Data Generation"):
        st.write("Starting data generation...")
        try:
            # Run the data generation script
            result = subprocess.run(["python", "data2.py"], capture_output=True, text=True)
            
            # Display the output or success message
            st.success("Data generation script executed successfully!")
            st.text(result.stdout)
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Other Streamlit components
    st.write("This is the main functionality of your application.")

if __name__ == "__main__":
    main()
