import requests

def ask_subnet_question(cidr: str):
    url = "http://localhost:8000/subnet/calculate"
    response = requests.post(url, json={"cidr": cidr})
    return response.json()

if __name__ == "__main__":
    cidr_input = input("Enter a CIDR (e.g., 192.168.1.0/24): ")
    result = ask_subnet_question(cidr_input)
    print("Subnet Calculation Result:")
    for k, v in result.items():
        print(f"{k}: {v}")