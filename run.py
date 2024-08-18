from app import create_app
from app.models import index_files

app = create_app()

if __name__ == '__main__':
    # Change this path to the directory you want to index
    index_files('D:/NOTARISWEB/file_index.db')  
    app.run(debug=True)
