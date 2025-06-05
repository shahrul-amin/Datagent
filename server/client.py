import requests


def delete_all():
    print('Deleding previous uploads')
    response = requests.post('http://127.0.0.1:5000/delete')
    print(response.text)

def upload():
    file_path = 'video games sales.csv'
    
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        response = requests.post('http://127.0.0.1:5000/upload', files=files)
        print(response.text)

def question():
    print("Enter a question")
    header = {'question': input(),
              'debug': 'True'}
    response = requests.get('http://127.0.0.1:5000/query/text', headers=header)
    print(response.text)

def code():
    print("Enter code request")
    header = {'question': input()}
    response = requests.get('http://127.0.0.1:5000/query/code', headers=header)
    print(response.text)

def execute():
    print('executing code')
    response = requests.get('http://127.0.0.1:5000/query/execute')
    print(response.text)

def main():
    # delete_all()
    print('Loading video games dataset')
    # upload()
    # code()
    while (True):
        question()
    # execute()

if __name__ == '__main__':
    main()
