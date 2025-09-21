def hello():
    return "Hello from example.py!"

def echo_file(file):
    content = file.read().decode("utf-8")
    return {"file_content": content}
