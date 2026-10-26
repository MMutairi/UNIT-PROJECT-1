# AutoCare Workshop Management System

## 1. What Is the System?

AutoCare is a terminal-based workshop management system developed using Python. It helps an automotive repair workshop organize daily operations, from customer registration to repair completion and payment processing.

The project demonstrates Python programming, Object-Oriented Programming (OOP), SQL databases, and relationships between database tables.

The system consists of six departments that work together using one centralized SQLite database.

## 2. Features

AutoCare includes six departments:

### Administrator
- Create and manage employee accounts.
- Assign employee roles and permissions.
- Activate or deactivate accounts.
- Reset employee passwords.
- Manage individual employee permissions.
- Link mechanic accounts to workshop mechanic records.

### Reception
- Register new customers.
- Register customer vehicles.
- Search for customers.
- View registered vehicles.

### Service Advisor
- Create repair tickets.
- Register mechanics.
- Assign repair tickets to mechanics.
- View repair tickets and their statuses.

### Mechanic
- View assigned repair tickets.
- Record repair diagnoses.
- Update repair status.
- Access only tickets assigned to the logged-in mechanic.

### Inventory
- Add spare parts.
- View and update stock quantities.
- Issue spare parts to repair tickets.
- Monitor low-stock items.

### Cashier
- Generate repair invoices.
- Calculate spare parts, labor costs, and VAT.
- Record customer payments.
- View unpaid invoices.
- View payment history.

### Additional Features
- Employee authentication.
- Password hashing.
- Role-Based Access Control (RBAC).
- Input validation and error handling.
- Relational database management.

## 3. Tools and Technologies

| Technology | Purpose |
|---|---|
| Python 3.11 | Main programming language |
| SQLite | Relational database |
| SQLAlchemy ORM | Database operations and relationships |
| OOP | Organizing application models |
| pwdlib / Argon2 | Secure password hashing |
| Visual Studio Code | Development environment |
| Git | Version control |
| GitHub | Source code repository |

## 4. How the System Works

AutoCare begins with employee authentication. After logging in, users can access departments according to their assigned roles and permissions.

Each department performs specific operations while sharing the same database.

### Workshop Scenario

1. **Reception:** A customer arrives with a vehicle that requires maintenance. Customer and vehicle information is registered.
2. **Service Advisor:** A repair ticket is created with a description of the problem and assigned to a mechanic.
3. **Mechanic:** The assigned mechanic accesses the repair ticket, starts the repair, and records the diagnosis.
4. **Inventory:** Required spare parts are issued to the repair ticket, and stock quantities are updated automatically.
5. **Mechanic:** Once the work is finished, the repair ticket is marked as completed.
6. **Cashier:** An invoice is generated based on spare parts, labor costs, and tax. The customer payment is recorded.

### Repair Ticket Status

**Pending → In Progress → Completed**

### Database Relationships

The system uses relational database tables to connect:

- Customers and vehicles.
- Vehicles and repair tickets.
- Mechanics and assigned repairs.
- Employee login accounts and mechanic records.
- Repair tickets and spare parts.
- Repair tickets and invoices.
- Invoices and payments.
- Employees, roles, and permissions.

### Database Location

The SQLite database is automatically created at:

`app/database/autocare.db`

The system uses **15 related database tables**, including customers, vehicles, repair tickets, mechanics, spare parts, invoices, payments, users, roles, permissions, and mechanic account mappings.

### Running the System

Install Python 3.11 and open the project folder in a VS Code terminal.

**Step 1 — Create and activate a virtual environment**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Step 2 — Install dependencies**

```powershell
python -m pip install -r requirements.txt
```

**Step 3 — Create database tables**

```powershell
python -m app.database.init_db
```

**Step 4 — Initialize roles and permissions**

```powershell
python -m app.database.seed_permissions
```

**Step 5 — Create the initial Administrator account**

```powershell
python -m app.auth.create_admin
```

**Step 6 — Run the application**

```powershell
python -m app.main
```

Database initialization and Administrator creation are only required during initial setup of a new database.

After setup, the application can be started using:

```powershell
python -m app.main
```

**Note:** The SQLite database is stored locally and should not be included in a public GitHub repository. A new database can be created using the setup commands above.

## 5. Possible Future Improvements

The system can be expanded with additional features such as:

- **Graphical User Interface (GUI):** Replace terminal menus with a desktop or web interface.
- **Customer Portal:** Allow customers to track repairs and view invoices.
- **Reports and Analytics:** Generate financial reports, repair statistics, and inventory summaries.
- **Appointment Scheduling:** Allow customers to schedule workshop appointments.
- **Notifications:** Send updates when repairs are completed or inventory is low.
- **AI Assistant:** Help employees navigate the application and find information.
- **Database Expansion:** Support PostgreSQL and multiple connected computers.
- **Advanced Repair Management:** Add repair priorities, estimated completion times, and maintenance history.

AutoCare is a Python-based workshop management prototype designed to demonstrate database integration, modular programming, authentication, and real-world business workflows.