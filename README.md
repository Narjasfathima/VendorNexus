# Vendor-Management-System

Setup Instructions
  -> Create a directory, open cmd in directory path  and clone VendorNexus project
      git clone https://github.com/Narjasfathima/VendorNexus.git
      
  -> Install Virtual environment
      pip install virtualenv
      
  -> Create virtual environment within the directory. 
      python -m venv venv_name  # On Windows
      python3 -m venv venv_name  # On macOS/Linux
      
  -> Activate virtual environmant     
      venv_name\Scripts\activate       # On Windows           
      source venv_name/bin/activate     # On macOS/Linux

  -> Install requirements.txt
      pip install -r requirements.txt

 -> Open VendorNexus in VScode
     code .

 -> Open terminal in vscode, Run the server and follow link
      py manage.py runserver


API Endpoints
1)Registration
    Endpoint: /api/user/
    
    Method:
        POST: Create a new user account.
        
    Data:JSON 
        {"username": "string","password": "string","email": "user@example.com"}

2)Token Generation for registered users
    Endpoint: /token/
    Method:
        POST: Create a token for registered user account.
    Data:JSON 
        {"username": "string","password": "string"}

3)Vendor Management
    a)  Method: POST (Create a vendor)
        Endpoint: /api/vendors/
        Data:JSON 
          {"name": "string", "contact_details": "string", "address": "string"}
    b)  Method: GET (List details of all vendors)
        Endpoint: /api/vendors/
    c)  Method: GET (Retrieve details of a specific vendor)
        Endpoint: /api/vendors/{id}/
    d)  Method: PUT (Update details of a specific vendor)
        Endpoint: /api/vendors/{id}/
        Data:JSON 
          {"name": "string", "contact_details": "string", "address": "string"}
    e)  Method: DELETE (Delete details of a specific vendor)
        Endpoint: /api/vendors/{id}/
    f)  Method: GET (Retrieve calculated performance metrics for a specific vendor)
        Endpoint: /api/vendors/{id}/performance/
        
4)Purchase Order Management
    a)  Method: POST (Create a Purchase order)
        Endpoint: /api/purchase_orders/
        Data:JSON 
          {"vendor": 0,"order_date": "2023-12-02T14:28:05.814Z","delivery_date": "2023-12-02T14:28:05.814Z","items": "string", "quantity": 0,"status": "string","quality_rating": 0,
          "issue_date": "2023-12-02T14:28:05.814Z", "acknowledgment_date": "2023-12-02T14:28:05.814Z"}
    b)  Method: GET (List all purchase orders)
        Endpoint: /api/purchase_orders/
    c)  Method: GET (List all purchase orders with an option to filter by vendor.)
        Endpoint: /api/purchase_orders/?vendor_id={id}/
    d)  Method: GET (Retrieve details of a specific purchase order)
        Endpoint: /api/purchase_orders/{id}/
    e)  Method: PUT (Update details of a specific purchase order)
        Endpoint: /api/purchase_orders/{id}/
        Data:JSON 
          {"vendor": 0,"order_date": "2023-12-02T14:28:05.814Z","delivery_date": "2023-12-02T14:28:05.814Z","items": "string", "quantity": 0,"status": "string","quality_rating": 0,
          "issue_date": "2023-12-02T14:28:05.814Z", "acknowledgment_date": "2023-12-02T14:28:05.814Z"}
    f)  Method: DELETE (Delete details of a specific purchase order)
        Endpoint: /api/purchase_orders/{id}/
    g)  Method: POST (Acknowledge a purchase order and update acknowledgment date.)
        Endpoint: /api/purchase_orders/{id}/acknowledge/


Test suite Instruction
  ->Run the test 
      py manage.py test vendor.tests
