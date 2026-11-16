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
4. Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (redirects automatically to `/customers`).

---

## Step 1: Inspect the Customer Directory (List View & Sorting)
**Time: 30 seconds**

1. Notice the **Customer Directory** showing 15 seeded customer records with clean pagination (10 per page).
2. Point out table columns: **ID**, **Name**, **Email**, **Phone**, **City**, **Registered Date**, and **Actions**.
3. Click on the column header **Name** to toggle ascending / descending alphabetical sort.
4. Click **Next &raquo;** at the bottom pagination bar to view page 2 (customers #11–15), then click **&laquo; Prev** to return to page 1.

---

## Step 2: Test Search Filtering
**Time: 45 seconds**

1. In the search box at the top, type `london` and press Enter (or click **Search**).
   - Notice the count updates to: `Found 1 matching customer`.
   - The table displays **Marcus Vance** (London, United Kingdom).
2. Now search for a partial phone number: `0199`.
   - The table displays **Elena Rostova** (`+1 416 555 0199`).
3. Search for a full name: `Amara Kowalski`.
   - The table instantly locates her profile.
4. Search for an unmatched query: `NonExistentPerson`.
   - Observe the friendly empty state: *"No results found for 'NonExistentPerson'"*.
5. Click **Clear Search Filter** to restore the full directory.

---

## Step 3: Trigger Field Validation Errors
**Time: 45 seconds**

1. Click **+ Add Customer** in the top navigation bar.
2. Enter the following deliberately invalid sample data:
   - **First Name**: `J` *(Too short, min 2 chars)*
   - **Last Name**: `D0e` *(Contains digit 0, letters only)*
   - **Email**: `invalid-email-format` *(Missing @ and domain)*
   - **Phone**: `123` *(Fewer than 7 digits)*
   - **City**: `Seattle`
3. Click **Register Customer**.
4. Observe the results:
   - Form is re-displayed with HTTP status 422.
   - Field-level red error messages appear directly below each invalid field.
   - What the user already typed (`J`, `D0e`, `Seattle`) is **preserved** without data loss.

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
   - The server rejects the submission with a friendly error message: *"A customer with this email address is already registered."*

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
   - Green flash message appears: *"Customer Sarah Connor added successfully."*
   - Redirects to the customer directory where **Sarah Connor** now appears.

---

## Step 6: View Profile Details and Edit Customer
**Time: 45 seconds**

1. Click **View** next to Sarah Connor (or click her name).
2. Review the profile detail view showing all fields, formatted phone link (`tel:`), email link (`mailto:`), and timestamp.
3. Click **Edit**.
4. Observe that all fields are pre-filled with Sarah's current values.
5. Update her details:
   - **City**: `Dallas`
   - **Phone**: `+1 (555) 999-0000`
   - *(Keep the email `sarah.connor@skyline.org` unchanged to demonstrate that self-email is ignored in duplicate checks)*
6. Click **Save Changes**.
7. Observe the green flash alert: *"Customer Sarah Connor updated successfully."*, and observe the updated City (`Dallas`) and phone number.

---

## Step 7: Safe Customer Deletion with Confirmation
**Time: 30 seconds**

1. From Sarah's profile page, click **Delete**.
2. Notice you are redirected to the dedicated confirmation page:
   - Clear warning: *"Are you sure you want to permanently delete this customer record? This action cannot be reversed."*
   - Shows summary details for Customer ID #16.
3. Click **Yes, Delete Customer** (sends a POST request).
4. Observe:
   - Green flash alert: *"Customer Sarah Connor was successfully deleted."*
   - Redirects to directory; Sarah Connor is gone from the database.

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
