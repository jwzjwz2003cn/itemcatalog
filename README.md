## Item Catalog Site
A Web Application that displays list of items within a variety of categories,
as well as provide a google login system

### Prerequsites
1. Make sure Virtualbox and vagrant are installed. 
2. Download FSND-Virtual-Machine.zip using the link https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip
3. Extract the downloaded zip file and go to the /vagrant directory
4. Start the virtual machine, it might take a few minutes to complete
```
$  vagrant up
```
5. Create a new directory called /catalog under /vagrant, and have all the code downloaded to this newly created directory .

## Usage
1. Create the database required for this web application 
```
$  python database_setup.py
```
2. Populate database with some data to start with
```
$  python loadData.py
```
3. Start the web application
```
$  python project.py
```
4. Visit the website at http://localhost:8000
5. Login using your google ID to reveal the 'Add Item' button

###REST API
- /catalog/
- /catalog/{category_name}/items
- /catalog/new/
- /catalog/{item_name}/edit
- /catalog/{item_name}/delete
- /catalog/{category_name}/{item_name}/edit

###JSON End-point
- http://localhost:8000/catalog.json/
- http://localhost:8000/catalog/{category_name}.json/  (Case sensitive)
- http://localhost:8000/catalog/{category_name}/{item_name}.json/ (Case sensitive)

###Clean up
- Remove the database
```
$  python clear_database.py
```