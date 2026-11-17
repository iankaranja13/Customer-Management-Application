# CustomerHub - 3-to-5 Minute Demo & Evaluation Script

This script walks through every feature of the Customer Management Application end-to-end. Follow these exact steps during viva or live project demonstrations.

---

## Preparation (Before Starting)

1. Open your terminal in the project directory:
   ```bash
   cd Customer-Management-Application
   source .venv/bin/activate
   ```
2. Reset and seed fresh sample data:
   ```bash
   flask --app run.py init-db
   python seed.py
   ```
3. Start the application:
   ```bash
   python run.py
   ```
   (If port 5000 is occupied on macOS, use `PORT=5001 python run.py` instead.)
4. Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (redirects automatically to `/customers`).

---

## Step 1: Inspect the Dashboard (Sidebar, Stats & Directory)
**Time: 45 seconds**

1. Notice the app shell: slim sidebar with CustomerHub branding and the active **Customers** section, plus a compact top bar with the page breadcrumb.
2. Point out the three live metric cards: **Total Customers** (15), **Recently Added** (last 30 days), and **Cities Represented** (unique cities) — all calculated from the database.
3. Point out directory columns: **Customer** (avatar initials + full name), **Email**, **Phone**, **City**, **Date Registered**, and the per-row **⋯ actions menu**.
4. Click the **Customer** column header to toggle ascending / descending alphabetical sort.
5. Use the **Show ... per page** selector to switch between 10, 25, and 50 rows.
6. Click **Next &raquo;** in the pagination bar to view page 2, then **&laquo; Prev** to return.

---

## Step 2: Test Live Search Filtering
**Time: 45 seconds**

1. In the search box, type `london` and watch the list filter live (or press **Search**).
   - Notice the count updates to: `Found 1 matching customer`.
   - The table displays **Marcus Vance** (London).
2. Search for a partial phone number: `0199`.
   - The table displays **Elena Rostova**.
3. Search for a full name: `Amara Kowalski`.
   - The table instantly locates her profile.
4. Search for an unmatched query: `NonExistentPerson`.
   - Observe the friendly empty state: *"No results found for 'NonExistentPerson'"*.
5. Click **Clear** (or **Clear Search Filter**) to restore the full directory.

---

## Step 3: Trigger Field Validation Errors
**Time: 45 seconds**

1. Click **Add Customer** — a registration modal opens.
2. Enter the following deliberately invalid sample data:
   - **First Name**: `J` *(Too short, min 2 chars)*
   - **Last Name**: `D0e` *(Contains digit 0, letters only)*
   - **Email**: `invalid-email-format` *(Missing @ and domain)*
   - **Phone**: `123` *(Fewer than 7 digits)*
   - **City**: `Seattle`
3. Click **Register Customer**.
4. Observe the results:
   - Inline red error messages appear directly below each invalid field.
   - The server is the final authority: the same rules are enforced backend-side (HTTP 422 on the dedicated `/customers/new` page without JavaScript).
   - What the user already typed is **preserved** without data loss.

---

## Step 4: Trigger Duplicate Email Rejection
**Time: 30 seconds**

1. Now enter valid data, but use an email that already exists in the system:
   - **First Name**: `Sarah`
   - **Last Name**: `Connor`
   - **Email**: `zoe.obrien@apextech.com` *(Already registered for Zoë O'Brien)*
   - **Phone**: `+1 (555) 345-6789`
2. Click **Register Customer**.
3. Observe the result:
   - The submission is rejected with a friendly inline error: *"A customer with this email address is already registered."*

---

## Step 5: Successfully Register a New Customer
**Time: 30 seconds**

1. Change the email to a unique address:
   - **First Name**: `Sarah`
   - **Last Name**: `Connor`
   - **Email**: `sarah.connor@skyline.org`
   - **Phone**: `+1 (555) 345-6789`
   - **Address**: `42 Tech Boulevard`
   - **City**: `Austin`
   - **Country**: `United States`
2. Click **Register Customer**.
3. Observe the result:
   - The modal closes and a green success toast appears: *"Customer Sarah Connor added successfully."*
   - The directory refreshes with **Sarah Connor** listed, and the **Total Customers** card updates to 16.

---

## Step 6: View Profile Drawer and Edit Customer
**Time: 45 seconds**

1. Open the **⋯** actions menu next to Sarah Connor and click **View** (or click her name).
2. A profile drawer slides in showing her avatar, Customer ID, email (`mailto:`), phone (`tel:`), city, and registration date.
3. Click **Edit** in the drawer — the edit modal opens with all fields pre-filled.
4. Update her details:
   - **City**: `Dallas`
   - **Phone**: `+1 (555) 999-0000`
   - *(Keep the email `sarah.connor@skyline.org` unchanged to demonstrate that self-email is ignored in duplicate checks)*
5. Click **Save Changes**.
6. Observe the green success toast: *"Customer Sarah Connor updated successfully."*, with the updated City (`Dallas`) and phone number in the directory. Her customer ID is unchanged.

---

## Step 7: Safe Customer Deletion with Confirmation
**Time: 30 seconds**

1. From the **⋯** actions menu next to Sarah Connor, click **Delete**.
2. A confirmation dialog appears:
   - Title: *"Delete this customer?"*
   - Warning: *"Are you sure you want to permanently delete Sarah Connor? This action cannot be undone."*
3. Click **Delete Customer**.
4. Observe:
   - Green success toast: *"Customer Sarah Connor was successfully deleted."*
   - The directory and dashboard metrics update; Sarah Connor is gone and remaining IDs stay sequential.

---

## Step 8: Verify SQLite File and Inspect Data
**Time: 30 seconds**

In a second terminal window (or stop the app with `Ctrl+C`):
1. Query the database directly using `sqlite3`:
   ```bash
   sqlite3 customers.db "SELECT id, first_name, last_name, email, phone, city FROM customers ORDER BY id DESC LIMIT 5;"
   ```
2. Inspect schema and indexes:
   ```bash
   sqlite3 customers.db ".schema"
   ```
   Point out `idx_customers_email` and `idx_customers_last_name`.

---

## Step 9: Review Git Branch History
**Time: 30 seconds**

Display the Git branching and conventional commit history:
```bash
git log --oneline --graph --all
```
Point out:
- Each feature was created on its own dedicated `feature/*` branch.
- Each branch followed the Conventional Commits specification.
- Each branch was merged into `develop` with `--no-ff` merge commits.
- Final release merge into `main` tagged with `v1.0.0`.
