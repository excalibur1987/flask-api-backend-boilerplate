python3 -m venv env

source ./env/bin/activate

pip install -r ./requirements/development.txt

pre-commit install

touch .env
echo 'export Sercret_KEY="your secret key here"' >> .env
echo 'export DATABASE_URL="your database connection string"' >> .env
echo 'export FLASK_APP="autoapp:app"' >> .env
echo 'export TZ="UTC"' >> .env

source .env

mkdir .vscode

touch .vscode/launch.json

echo '{\n\t"version": "0.2.0",\n\t"configurations": [' >> .vscode/launch.json
echo '\t\t{\n\t\t\t"name": "Python: Flask",\n' >> .vscode/launch.json
echo '\t\t\t"type": "python",\n\t\t\t"request": "launch",\n' >> .vscode/launch.json
echo '\t\t\t"module": "flask",\n\t\t\t"env": {' >> .vscode/launch.json
echo '\t\t\t\t"FLASK_APP": "autoapp:app",' >> .vscode/launch.json
echo '\t\t\t\t"FLASK_ENV": "development"' >> .vscode/launch.json
echo '\t\t\t},\n\t\t\t"args": ["run", "--no-debugger"],' >> .vscode/launch.json
echo '\n\t\t\t"jinja": true\n\t\t}\n\t]\n}' >> .vscode/launch.json


sed -i 's+\t+    +g' .vscode/launch.json

echo "Edit your .env file then source it & run 'flask db upgrade'"

rm ./intialize.sh
git add .
git commit --amend -m "initial commit"
git push --force